from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction

from tutor.models import ClassLearners
from .models import Quiz, Question, QuizAttempt, UserAnswer
from administration.models import Learner, PastQuestionPaper
from django.db.models import Sum

# Create your views here.
@login_required()  # Ensures only authenticated users can access this view
def index_view(request):
    # Load any success/error/info messages from previous requests
    user = request.user
    classes = []
    if Learner.objects.filter(learner=user).exists():
        learner = Learner.objects.get(learner=user)
        all_classes = ClassLearners.objects.all()
        for class_learner in all_classes:
            if learner in [class_learner.learner_1, class_learner.learner_2, class_learner.learner_3, class_learner.learner_4, class_learner.learner_5]:
                class_instance = class_learner.class_name
                classes.append(class_instance)
    else:
        messages.success(request, "You are not enrolled in any class yet. Please contact your tutor to enroll you.")
        return render(request, 'learner/index.html', {
            'messages': messages.get_messages(request),
        })
            
    messages_to_display = messages.get_messages(request)
    return render(request, 'learner/index.html', {
        'messages': messages_to_display,
        'classes': classes
    })
@login_required()
def view_quizzes_view(request):
    user = request.user
    if Learner.objects.filter(learner=user).exists():
        learner = Learner.objects.get(learner=user)
        subjects = [s for s in [learner.subject1, learner.subject2, learner.subject3] if s]
        tutors = [t for t in [learner.tutor1, learner.tutor2, learner.tutor3] if t]
        quizzes = Quiz.objects.filter(subject__in=subjects, subject__tutor__in=tutors)
        
        return render(request,"learner/view_quizzes.html",{
        'quizzes': quizzes,
        'learner': learner
        })
    else:
        messages.success(request, "You are not enrolled in any class yet. Please contact your tutor to enroll you.")
        return render(request, 'learner/view_quizzes.html', {
            'messages': messages.get_messages(request)
        })
    
@login_required
def take_question(request, quiz_id, question_id):
    """Display and handle a specific quiz question"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    # Get or create quiz attempt
    quiz_attempt, _ = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz,
        defaults={'started_at': timezone.now()}
    )

    # Handle form submission
    if request.method == "POST":
        answer_value = request.POST.get("answer")
        action = request.POST.get("action")  # 'next' or 'finish'

        if not answer_value:
            messages.error(request, "Please select or enter an answer before proceeding.")
            return redirect('take_question', quiz_id=quiz.id, question_id=question.id)

        # Save or update user answer
        user_answer, _ = UserAnswer.objects.get_or_create(
            quiz_attempt=quiz_attempt,
            question=question
        )
        user_answer.user_answer = answer_value
        user_answer.auto_mark()  # auto mark if applicable

        # Go to next question or finish quiz
        all_questions = Question.objects.filter(quiz=quiz).order_by('question_number')
        next_question = all_questions.filter(question_number__gt=question.question_number).first()

        if action == 'next' and next_question:
            return redirect('take_question', quiz_id=quiz.id, question_id=next_question.id)
        else:
            return redirect('finish_quiz', quiz_id=quiz.id)

    # GET request: display question
    all_questions = Question.objects.filter(quiz=quiz).order_by('question_number')
    total_questions = all_questions.count()
    next_question = all_questions.filter(question_number__gt=question.question_number).first()
    previous_question = all_questions.filter(question_number__lt=question.question_number).last()

    answers = question.answer_set.all() if question.question_type == 1 else []
    user_answer = UserAnswer.objects.filter(quiz_attempt=quiz_attempt, question=question).first()
    answered_questions = UserAnswer.objects.filter(quiz_attempt=quiz_attempt).count()

    context = {
        'quiz': quiz,
        'question': question,
        'answers': answers,
        'next_question': next_question,
        'previous_question': previous_question,
        'total_questions': total_questions,
        'user_answer': user_answer,
        'answered_questions': answered_questions,
    }

    return render(request, 'learner/take_question.html', context)


@login_required
def submit_answer(request, quiz_id, question_id):
    """Handle answer submission"""
    if request.method != 'POST':
        return redirect('take_question', quiz_id=quiz_id, question_id=question_id)

    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    answer_text = request.POST.get('answer', '').strip()
    action = request.POST.get('action', 'save')

    # Allow empty answers only if finishing
    if not answer_text and action != 'finish':
        messages.error(request, "Please provide an answer.")
        return redirect('take_question', quiz_id=quiz_id, question_id=question_id)

    quiz_attempt, _ = QuizAttempt.objects.get_or_create(
        user=request.user,
        quiz=quiz,
        defaults={'started_at': timezone.now()}
    )

    if answer_text:
        with transaction.atomic():
            user_answer, _ = UserAnswer.objects.update_or_create(
                quiz_attempt=quiz_attempt,
                question=question,
                defaults={
                    'user_answer': answer_text,
                    'answered_at': timezone.now(),
                }
            )
            user_answer.auto_mark()
            quiz_attempt.calculate_score()

    if action == 'next':
        all_questions = Question.objects.filter(quiz=quiz).order_by('question_number')
        next_question = all_questions.filter(question_number=question.question_number + 1).first()
        if next_question:
            return redirect('take_question', quiz_id=quiz_id, question_id=next_question.id)
        return redirect('finish_quiz', quiz_id=quiz_id)

    elif action == 'finish':
        return redirect('finish_quiz', quiz_id=quiz_id)

    return redirect('take_question', quiz_id=quiz_id, question_id=question_id)


@login_required

def finish_quiz(request, quiz_id):
    """Finish the quiz, calculate scores, and show results"""
    
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Get the quiz attempt for this user
    try:
        quiz_attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz)
    except QuizAttempt.DoesNotExist:
        messages.error(request, "You haven't started this quiz yet.")
        return redirect('quiz_detail', quiz_id=quiz_id)

    # If already completed, redirect to results
    if quiz_attempt.is_completed:
        return redirect('quiz_result', quiz_id=quiz_id)

    # Mark attempt as completed
    quiz_attempt.completed_at = timezone.now()
    quiz_attempt.is_completed = True
    quiz_attempt.save()

    # Fetch all user answers for this attempt
    user_answers = UserAnswer.objects.filter(quiz_attempt=quiz_attempt).select_related('question')

    # Auto-mark MCQ / True-False answers
    for ua in user_answers:
        ua.auto_mark()
        # Attach correct answer for template display
        if ua.question.question_type in [1, 2]:
            ua.correct_answer = ua.question.answer_set.filter(is_right=True).first()

    # Calculate total score
    quiz_attempt.calculate_score()

    # Quiz statistics
    total_questions = quiz.question_set.count()
    answered_questions = user_answers.count()
    correct_answers = user_answers.filter(is_correct=True).count()
    total_possible_marks = quiz.question_set.aggregate(total=Sum('mark'))['total'] or 0
    needs_marking = user_answers.filter(needs_marking=True)

    context = {
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
        'user_answers': user_answers,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'total_possible_marks': total_possible_marks,
        'needs_marking': needs_marking,
    }

    return render(request, 'learner/quiz_result.html', context)

@login_required
def quiz_result(request, quiz_id):
    """Display quiz results"""
    quiz = get_object_or_404(Quiz, id=quiz_id)

    try:
        quiz_attempt = QuizAttempt.objects.get(user=request.user, quiz=quiz)
    except QuizAttempt.DoesNotExist:
        messages.error(request, "You haven't taken this quiz yet.")
        return redirect('quiz_detail', quiz_id=quiz_id)

    user_answers = UserAnswer.objects.filter(quiz_attempt=quiz_attempt).select_related('question')

    for ua in user_answers:
        if ua.question.question_type in [1, 2]:
            ua.correct_answer = ua.question.answer_set.filter(is_right=True).first()

    context = {
        'quiz': quiz,
        'quiz_attempt': quiz_attempt,
        'user_answers': user_answers,
    }
    return render(request, 'learner/quiz_result.html', context)

@login_required
def past_papers_subjects_view(request):
    user = request.user
    if not Learner.objects.filter(learner=user).exists():
        messages.info(request, "You are not enrolled yet.")
        return render(request, 'learner/past_papers_subjects.html')

    learner = Learner.objects.get(learner=user)

    subjects = [
        s for s in [learner.subject1, learner.subject2, learner.subject3] if s
    ]

    return render(request, 'learner/past_papers_subjects.html', {'subjects': subjects})

@login_required
def past_papers_years_view(request, subject_id):
    user = request.user
    learner = Learner.objects.get(learner=user)
    subjects = [s for s in [learner.subject1, learner.subject2, learner.subject3] if s]

    # Ensure learner has access to this subject
    subject = next((s for s in subjects if s.id == subject_id), None)
    if not subject:
        messages.error(request, "You do not have access to this subject.")
        return redirect('learner:past_papers_subjects')

    # Get all years with visible past papers
    years = PastQuestionPaper.objects.filter(
        subject=subject
    ).values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'learner/past_papers_years.html', {
        'subject': subject,
        'years': years
    })

@login_required
def past_papers_list_view(request, subject_id, year):
    user = request.user
    learner = Learner.objects.get(learner=user)
    subjects = [s for s in [learner.subject1, learner.subject2, learner.subject3] if s]

    # Ensure learner has access
    subject = next((s for s in subjects if s.id == subject_id), None)
    if not subject:
        messages.error(request, "You do not have access to this subject.")
        return redirect('learner:past_papers_subjects')

    # Get past papers for that subject & year
    past_papers = PastQuestionPaper.objects.filter(
        subject=subject,
        year=year
    ).order_by('paper_number')

    return render(request, 'learner/past_papers_list.html', {
        'subject': subject,
        'year': year,
        'past_papers': past_papers
    })
