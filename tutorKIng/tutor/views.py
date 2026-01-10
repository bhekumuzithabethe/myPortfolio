from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required

from administration.models import PastQuestionPaper
from .forms import ClientForm, PaymentForm,AnswerFormSet,QuestionForm,QuizForm,SubjectForm, ReferrerForm, ClassForm, ClassLearnersForm
from django.contrib import messages
from .models import Month, Quiz,Question,Answer,Subject, Class,ClassLearners
from datetime import datetime
from django.forms import inlineformset_factory
from django.http import JsonResponse
import os
import google.generativeai as genai
from django.conf import settings

# =============================
# Index View (Dashboard for Tutors)
# =============================
@login_required()  # Ensures only authenticated users can access this view
def index_view(request):
    # Load any success/error/info messages from previous requests
    classes = Class.objects.filter(tutor=request.user)

    messages_to_display = messages.get_messages(request)
    return render(request, 'tutor/index.html', {
        'messages': messages_to_display,
        'classes_instance': classes
    })


# Configure the Gemini API (make sure to set your API key in settings or environment)
def configure_gemini():
    """Configure Gemini API with API key"""
    try:
        # Try to get API key from settings or environment variable
        api_key=[os.environ['GOOGLE_GEMINI_API_KEY']]
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in settings or environment variables")
        
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Gemini configuration error: {e}")
        return False

# Configure on import
GEMINI_CONFIGURED = configure_gemini()

@login_required
def chatbot_view(request):
    """Main chatbot view with conversation history"""
    
    if request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                message = request.POST.get('message', '').strip()
                
                if not message:
                    return JsonResponse({
                        'success': False,
                        'error': 'Message cannot be empty'
                    }, status=400)
                
                # Get conversation history from session
                conversation_history = request.session.get('chat_history', [])
                
                # Add user message to history
                conversation_history.append({
                    'role': 'user',
                    'content': message,
                    'timestamp': str(request.user.id)  # Simple timestamp
                })
                
                # Get response from Gemini
                response_text = ask_geminai(message, conversation_history)
                
                # Add AI response to history
                conversation_history.append({
                    'role': 'assistant',
                    'content': response_text,
                    'timestamp': str(request.user.id)
                })
                
                # Keep only last 20 messages to prevent session from getting too large
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]
                
                # Save updated history to session
                request.session['chat_history'] = conversation_history
                request.session.modified = True
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'response': response_text,
                    'history': conversation_history
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        # Handle non-AJAX POST requests
        else:
            message = request.POST.get('message', '').strip()
            response_text = ask_geminai(message)
            
            # Store in session for non-AJAX requests too
            chat_history = request.session.get('chat_history', [])
            chat_history.append({
                'role': 'user',
                'content': message,
                'timestamp': 'non-ajax'
            })
            chat_history.append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': 'non-ajax'
            })
            request.session['chat_history'] = chat_history
            
            return render(request, 'tutor/chatbot.html', {
                'user_message': message,
                'ai_response': response_text,
                'chat_history': chat_history
            })
    
    else:
        # GET request - initialize or clear conversation
        if 'clear_chat' in request.GET:
            # Clear chat history
            if 'chat_history' in request.session:
                del request.session['chat_history']
            messages.success(request, "Chat history cleared!")
        
        # Initialize with welcome message if new session
        chat_history = request.session.get('chat_history', [])
        
        if not chat_history:
            # Add initial welcome message
            welcome_message = "Hello! I'm your AI tutor assistant. How can I help you today?"
            chat_history.append({
                'role': 'assistant',
                'content': welcome_message,
                'timestamp': 'system'
            })
            request.session['chat_history'] = chat_history
        
        return render(request, 'tutor/chatbot.html', {
            'chat_history': chat_history,
            'gemini_configured': GEMINI_CONFIGURED
        })

def ask_geminai(message, conversation_history=None):
    """
    Get response from Gemini AI
    
    Args:
        message: Current user message
        conversation_history: Previous conversation context
    
    Returns:
        str: AI response
    """
    try:
        # Check if Gemini is configured
        if not GEMINI_CONFIGURED:
            return "Sorry, the AI service is not configured properly. Please contact the administrator."
        
        # Configure model with safety settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Create model with configuration
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Prepare conversation context
        chat_session = model.start_chat(history=[])
        
        if conversation_history and len(conversation_history) > 2:
            # Add previous context (skip the last user message which is the current one)
            for msg in conversation_history[:-1]:
                if msg['role'] == 'user':
                    chat_session.send_message(msg['content'])
                elif msg['role'] == 'assistant':
                    # For assistant messages, we need to simulate response
                    # In Gemini chat, we can't directly add assistant messages
                    # So we'll use a different approach
                    pass
        
        # Send current message
        response = chat_session.send_message(message)
        
        # Process response
        if response.candidates and len(response.candidates) > 0:
            if response.candidates[0].finish_reason == 'SAFETY':
                return "I cannot respond to that request as it may violate content safety policies."
            
            response_text = response.candidates[0].content.parts[0].text
            
            # Clean up response
            response_text = response_text.replace('*', ' ').strip()
            
            # Format response for better readability
            response_text = format_response(response_text)
            
            return response_text
        else:
            return "I'm sorry, I couldn't generate a response. Please try again."
        
    except genai.types.generation_types.BlockedPromptException:
        return "I cannot respond to that request as it may violate content safety policies."
    
    except genai.types.generation_types.StopCandidateException:
        return "The response was stopped. Please try rephrasing your question."
    
    except Exception as e:
        print(f"Gemini API error: {e}")
        
        # Return user-friendly error messages
        if "API key" in str(e):
            return "API configuration error. Please contact the administrator."
        elif "quota" in str(e).lower():
            return "API quota exceeded. Please try again later."
        elif "network" in str(e).lower():
            return "Network error. Please check your connection and try again."
        else:
            return f"Sorry, something went wrong: {str(e)}"

def format_response(text):
    """Format the AI response for better readability"""
    # Replace markdown-like formatting
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Handle bullet points
        if line.strip().startswith('- '):
            line = '• ' + line.strip()[2:]
        # Handle numbered lists
        elif line.strip() and line.strip()[0].isdigit() and '. ' in line[:4]:
            # Keep numbered lists as is
            pass
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

# Additional view for clearing chat history
@login_required
def clear_chat_history(request):
    """Clear the chat history"""
    if 'chat_history' in request.session:
        del request.session['chat_history']
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Chat history cleared'})
    else:
        messages.success(request, "Chat history cleared successfully!")
        return render(request, 'tutor/chatbot.html', {})

# View to export chat history
@login_required
def export_chat_history(request):
    """Export chat history as JSON"""
    chat_history = request.session.get('chat_history', [])
    
    response = JsonResponse(chat_history, safe=False)
    response['Content-Disposition'] = 'attachment; filename="chat_history.json"'
    return response

# =============================
# Payment Form Submission View
# =============================
@login_required()
def payment_form_view(request):
    now = datetime.now()
    month_name = now.strftime("%B %Y")  # Get current month as string, e.g. "June"

    # Check if the current month exists in the database
    if Month.objects.filter(current_month=month_name).exists():
        if request.method == 'POST':
            form = PaymentForm(request.POST, request.FILES)  # Handle file upload (proof of payment)
            
            if form.is_valid():
                referrers_full_name = form.cleaned_data['referrers_full_name'].lower()  # apply .lower() correctly
                cost_of_subscription = form.cleaned_data['cost_of_subscription']
                number_of_days_you_tutor_per_week = form.cleaned_data['number_of_days_you_tutor_per_week']

                payment = form.save(commit=False)

                if "nanick" in referrers_full_name or "ioline" in referrers_full_name:
                    payment.amount_due_to_referrer = 0.00
                    daily_amount = (cost_of_subscription * 0.7) / 5
                    payment.amount_due_to_tutor = daily_amount * number_of_days_you_tutor_per_week
                else:
                    before_referrer = cost_of_subscription * 0.7
                    payment.amount_due_to_referrer = before_referrer * 0.2
                    after_referrer = before_referrer * 0.8
                    daily_amount = after_referrer / 5
                    payment.amount_due_to_tutor = daily_amount * number_of_days_you_tutor_per_week

                user  = request.user
                users_full_name = f'{user.first_name} {user.last_name}'
                payment.month = Month.objects.get(current_month=month_name)
                payment.tutors_full_name = users_full_name
                payment.save()

                messages.success(request, f'{month_name} payment form added successfully')
                return redirect('tutor')
            else:
                messages.error(request, 'Failed to send your payment form')
                return render(request, 'tutor/forms/payment_form.html', {
                    'form': form,
                    'month_name': month_name,
                })

        else:
            # GET request: Display empty payment form
            form = PaymentForm()
            return render(request, 'tutor/forms/payment_form.html', {
                'form': form,
                'month_name': month_name,
            })
    else:
        # Current month is not found in DB — redirect to tutor dashboard
        messages.success(request, f'{month_name} payment forms are not available at the moment. Please check back later or contact support if you need assistance.')
        return redirect('tutor')

# =============================
# Client Form Submission View
# =============================
@login_required()
def client_form_view(request):
    now = datetime.now()
    month_name = now.strftime("%B %Y")

    if Month.objects.filter(current_month=month_name).exists():
        if request.method == 'POST':
            form = ClientForm(request.POST)

            if form.is_valid():
                # Create and save new Client instance using cleaned form data
                client = form.save(commit=False)
                client.month = Month.objects.get(current_month=month_name)
                client.save()
                messages.success(request, f'{month_name} client form added successfully')
                return redirect('tutor')
            else:
                # If form is invalid, redisplay with error messages
                messages.error(request, 'Please correct the errors below.')
                return render(request, 'tutor/forms/client_form.html', {
                    'form': form,
                    'month_name': month_name,
                })
        else:
            # GET request: Display empty client form
            form = ClientForm()
            return render(request, 'tutor/forms/client_form.html', {
                'form': form,
                'month_name': month_name,
            })
    else:
        messages.success(request, f'{month_name} client forms are not available at the moment. Please check back later or contact support if you need assistance.')
        return redirect('tutor')

@login_required()
def referrer_form_view(request):
    now = datetime.now()
    month_name = now.strftime("%B %Y")

    if Month.objects.filter(current_month=month_name).exists():
        if request.method == 'POST':
            form = ReferrerForm(request.POST)

            if form.is_valid():
                # Create and save new Referrer instance using cleaned form data
                referrer = form.save(commit=False)
                referrer.month = Month.objects.get(current_month=month_name)
                referrer.referrers_name = request.user                
                referrer.save()
                messages.success(request, f'{month_name} referrer form added successfully')
                return redirect('tutor')
            else:
                # If form is invalid, redisplay with error messages
                messages.error(request, 'Please correct the errors below.')
                return render(request, 'tutor/forms/referrer_form.html', {
                    'form': form,
                    'month_name': month_name,
                })
        else:
            # GET request: Display empty referrer form
            form = ReferrerForm()
            return render(request, 'tutor/forms/add_referrer.html', {
                'form': form,
                'month_name': month_name,
            })
    else:
        messages.success(request, f'{month_name} referrer forms are not available at the moment. Please check back later or contact support if you need assistance.')
        return redirect('tutor')

#Quizzes view_functions
    #Adding a new quiz view
@login_required(login_url="login")
def add_quiz_view(request):
    if request.method == 'POST':
        #Instantiating the quiz form
        form = QuizForm(request.POST, tutor=request.user)
        #If the user submitted valid input
        if form.is_valid():
            #Saving the quiz to the database
            new_quiz = form.save()
            #Success message
            messages.success(request, 'The quiz ('+form.cleaned_data['quiz_title']+') was successfully added.')
            #Getting the quiz we've just added, to redirect the teacher to the edit Quiz page when done
            return redirect('create_question', quiz_id=new_quiz.id)
            
        else:
            #If failed to add the quiz
            messages.error(request, 'Failed to add quiz.')
            return redirect('create_quiz')
    else:
        #Instantiating the quiz form
        form = QuizForm(tutor=request.user)
        return render(request,"tutor/forms/add_quiz.html",{
            'form' : form,
        })
@login_required(login_url="login")    
    #Updating a quiz details view
def edit_quiz_view(request,id):
    if request.method == "POST":
        #Getting the Quiz object the teacher wants to update
        quiz = Quiz.objects.get(pk=id)
        #Instantiating the quiz form and initializing the quiz details to update
        form = QuizForm(request.POST,instance=quiz)
        #If the user submitted valid input
        if form.is_valid():
            #Updating quiz details
            updated_subject = form.save()
            #Success message and redirecting to manage quizzes when done
            messages.success(request, 'Successfully updated quiz details.')
            return redirect('manage_quizzes')
        else:
            #If invalid details were submited by the teacher
            messages.error(request, 'Failed to updated quiz details.')
            return redirect('update_quiz',quiz)
    else:
        #Getting the quiz object
        quiz = Quiz.objects.get(pk=id)
        #Instantiating the quiz form initializing the quiz details to update
        form = QuizForm(instance=quiz)

        return render(request,"tutor/forms/update_quiz.html",{
            'form' : form,
            'quiz':quiz,
        })
    #Delete Quiz view
@login_required(login_url="login")
    #Delete quiz view
def delete_quiz_view(request,id):
    #Getting the quiz the teacher wants to delete
    quiz = Quiz.objects.get(pk=id)
    #delete quiz
    quiz.delete()
    #Success mmessage and redirecting to manage quizzes
    messages.success(request, 'Quiz deleted successfully.')
    return redirect('manage_quizzes')
@login_required(login_url="login")
    #Manage quizzes view
def manage_quizzes_view(request):
    #Getting all the Quiz objects
    user = request.user
    quizzes = Quiz.objects.filter(subject__tutor=user).all()
    return render(request,"tutor/manage/manage_quizzes.html",{
        'quizzes': quizzes,
    }) 

#Questions view_functions
@login_required(login_url="login")
    #Adding a new question view

def add_question_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        # Convert question_type to integer for comparison
        try:
            question_type = int(request.POST.get('question_type', 0))
        except (ValueError, TypeError):
            question_type = 0
        
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            
            # Handle different question types (using integers)
            if question_type == 1:  # Multiple Choice
                # Use the formset for multiple choice
                formset = AnswerFormSet(request.POST, instance=question)
                if formset.is_valid():
                    question.save()
                    formset.save()
                    messages.success(request, "Multiple choice question added successfully!")
                    return redirect('manage_questions', id=quiz.id)
                else:
                    # If formset is invalid, add errors to messages
                    for error in formset.errors:
                        messages.error(request, f"Answer error: {error}")
                    
            elif question_type == 2:  # True/False
                # Save True/False question
                question.save()
                
                # Create True and False answers
                correct_answer = request.POST.get('correct_true_false', 'True')
                
                Answer.objects.create(
                    question=question,
                    answer="True",
                    is_right=(correct_answer == "True")
                )
                
                Answer.objects.create(
                    question=question,
                    answer="False",
                    is_right=(correct_answer == "False")
                )
                
                messages.success(request, "True/False question added successfully!")
                return redirect('manage_questions', id=quiz.id)
                
            elif question_type == 3 or question_type == 4:  # Text or Paragraph Answer
                # Save text/paragraph question
                expected_answer = request.POST.get('expected_answer', '')
                question.save()
                
                # Create an answer record for the expected answer
                Answer.objects.create(
                    question=question,
                    answer=expected_answer,
                    is_right=True
                )
                
                messages.success(request, "Question added successfully!")
                return redirect('manage_questions', id=quiz.id)
            else:
                messages.error(request, "Please select a valid question type.")
        else:
            messages.error(request, "Please correct the errors below.")
            # Debug: print form errors
            print("Form errors:", form.errors)
    else:
        form = QuestionForm()
    
    formset = AnswerFormSet(instance=Question())
    
    return render(request, 'tutor/forms/add_question.html', {
        'form': form,
        'formset': formset,
        'quiz': quiz
    })

@login_required(login_url="login")    
    #Updating question details view
def edit_question_view(request, id):
    AnswerFormSet = inlineformset_factory(
    Question, Answer,
    fields=['answer', 'is_right'],
    can_delete=True,  # Enables deletion of answers
    extra=0
    )

    question = get_object_or_404(Question, pk=id)
    quiz = question.quiz

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Successfully updated question and answers.')
            return redirect('manage_questions', id=quiz.id)
        else:
            messages.error(request, 'Failed to update question details.')
            return redirect('update_question', id=id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

        return render(request, "tutor/forms/update_question.html", {
            'form': form,
            'formset': formset,
            'question': question,
            'quiz': quiz,
        })
#Delete quiz view
@login_required(login_url="login")
    #Delete quiz view
def delete_question_view(request,id):
    #Getting the Question object the teacher wants to delete        
    question = Question.objects.get(pk=id)
    #Deliting the question 
    question.delete()
    #Success message and redirecting to manage questions when done
    messages.success(request, 'Question deleted successfully.')
    return redirect('manage_quizzes')
@login_required()
def manage_questions_view(request, id):
    quiz = Quiz.objects.get(pk=id)
    questions = Question.objects.filter(quiz=quiz).all
    return render(request,'tutor/manage/manage_questions.html',{
        'questions':questions,
        'quiz':quiz
    })

@login_required()
def add_subject_view(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.tutor = request.user
            subject.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('tutor-manage-subjects')
    else:
        form = SubjectForm()
    return render(request, 'tutor/forms/add_subject.html', {
        'form': form
    })
@login_required()
def manage_subjects_view(request):
    subjects = Subject.objects.filter(tutor=request.user).all()
    return render(request, 'tutor/manage/manage_subjects.html', {
        'subjects': subjects
    })

@login_required()
def edit_subject_view(request, id):
    subject = get_object_or_404(Subject, id=id, tutor=request.user)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('tutor-manage-subjects')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'tutor/forms/edit_subject.html', {
        'form': form,
        'subject': subject
    })

@login_required()
def delete_subject_view(request, id):   
    subject = get_object_or_404(Subject, id=id, tutor=request.user)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('manage-subjects')
    return render(request, 'tutor/forms/delete_subject.html', {
        'subject': subject
    })

@login_required()
def add_class_view(request):
    if request.method == 'POST':
        form = ClassForm(request.POST, tutor=request.user)
        if form.is_valid():
            class_instance = form.save(commit=False)
            class_instance.tutor = request.user
            class_instance.save()
            messages.success(request, 'Class added successfully.')
            return redirect('tutor-manage-classes')
    else:
        form = ClassForm(tutor=request.user)
    return render(request, 'tutor/forms/add_class.html', {
        'form': form
    })

@login_required()
def manage_classes_view(request):
    classes = Class.objects.filter(tutor=request.user).all()
    return render(request, 'tutor/manage/manage_classes.html', {
        'classes': classes
    })

@login_required()
def edit_class_view(request, id):
    class_instance = get_object_or_404(Class, id=id, tutor=request.user)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_instance, tutor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully.')
            return redirect('tutor-manage-classes')
    else:
        form = ClassForm(instance=class_instance, tutor=request.user)
    return render(request, 'tutor/forms/edit_class.html', {
        'form': form,
        'class': class_instance
    })

@login_required()
def delete_class_view(request, id):
    class_instance = get_object_or_404(Class, id=id, tutor=request.user)
    if request.method == 'POST':
        class_instance.delete()
        messages.success(request, 'Class deleted successfully.')
        return redirect('tutor-manage-classes')
    return render(request, 'tutor/forms/delete_class.html', {
        'class': class_instance
    })

@login_required()
def add_class_learners_view(request):
    if request.method == 'POST':
        form = ClassLearnersForm(request.POST, tutor=request.user)
        if form.is_valid():
            class_learners = form.save(commit=False)
            class_learners.save()
            messages.success(request, ' Learners added successfully.')
            return redirect('tutor-manage-classes')
    else:
        form = ClassLearnersForm(tutor=request.user)
    return render(request, 'tutor/forms/add_class_learners.html', {
        'form': form
    })
@login_required()
def manage_class_learners_view(request, id):  
    class_instance = get_object_or_404(Class, id=id, tutor=request.user)
    class_learners = ClassLearners.objects.filter(class_name=class_instance).all()
    return render(request, 'tutor/manage/manage_class_learners.html', {
        'learners': class_learners,
        'class': class_instance
    })
@login_required()
def edit_class_learners_view(request, id):
    class_learners = get_object_or_404(ClassLearners, id=id)
    if request.method == 'POST':
        form = ClassLearnersForm(request.POST, instance=class_learners)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class learners updated successfully.')
            return redirect('tutor-manage-classes')
    else:
        form = ClassLearnersForm(instance=class_learners, tutor=request.user)
    return render(request, 'tutor/forms/edit_class_learners.html', {
        'form': form,
        'learners': class_learners
    })
@login_required()
def delete_class_learners_view(request, id):
    class_learners = get_object_or_404(ClassLearners, id=id, tutor=request.user)
    if request.method == 'POST':
        class_learners.delete()
        messages.success(request, 'Class learners deleted successfully.')
        return redirect('tutor-manage-classes')
    return render(request, 'tutor/forms/delete_class_learners.html', {
        'learners': class_learners
    })


@login_required
def past_papers_subjects_view(request):
    user = request.user
    subjects = Subject.objects.filter(tutor=user)
    return render(request, 'tutor/past_papers_subjects.html', {'subjects': subjects})

@login_required
def past_papers_years_view(request, subject_id):
    user = request.user
    subjects = Subject.objects.filter(tutor=user)

    # Ensure learner has access to this subject
    subject = next((s for s in subjects if s.id == subject_id), None)
    if not subject:
        messages.error(request, "You do not have access to this subject.")
        return redirect('tutor_past_papers_subjects')

    # Get all years with visible past papers
    years = PastQuestionPaper.objects.filter(
        subject=subject
    ).values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'tutor/past_papers_years.html', {
        'subject': subject,
        'years': years
    })

@login_required
def past_papers_list_view(request, subject_id, year):
    user = request.user
    subjects = Subject.objects.filter(tutor=user)

    # Ensure learner has access
    subject = next((s for s in subjects if s.id == subject_id), None)
    if not subject:
        messages.error(request, "You do not have access to this subject.")
        return redirect('tutor_past_papers_subjects')

    # Get past papers for that subject & year
    past_papers = PastQuestionPaper.objects.filter(
        subject=subject,
        year=year
    ).order_by('paper_number')

    return render(request, 'tutor/past_papers_list.html', {
        'subject': subject,
        'year': year,
        'past_papers': past_papers
    })
