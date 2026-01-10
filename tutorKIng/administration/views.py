from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from tutor.models import Payment,Month,Client,Subject, Class
from authentication.models import User
from datetime import datetime
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Learner
from .forms import LearnerForm, PastQuestionPaperForm
from tutor.models import ClassLearners

from django.db.models import Sum, F, Value, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce

# Create your views here.


# =============================
# Index View (Protected)
# =============================
@login_required()
def index_view(request):
    pending_count = User.objects.filter(approved='No').count()
    messages_to_display = messages.get_messages(request)
    return render(request, 'administration/index.html',{
        'messages':messages_to_display,
        'pending_count': pending_count
    })
@login_required()
def manage_payments_view(request):
    now = datetime.now()
    month = now.strftime("%B %Y")
    if Month.objects.filter(current_month=month).exists():
        payments = Payment.objects.all()
        return render(request, 'administration/manage/manage_payements.html',{
            'payments': payments,
            'month':month,
        })
    else:
        return redirect('administrator')
    
@login_required()
def manage_clients_view(request):
    now = datetime.now()
    month = now.strftime("%B %Y")
    if Month.objects.filter(current_month=month).exists():
        clients = Client.objects.all()
        return render(request, 'administration/manage/manage_clients.html',{
            'clients': clients,
            'month':month,
        })
    else:
        return redirect('administrator')
    
@login_required()
def manage_users_view(request):
    users = User.objects.all().exclude(user_type='Admin').order_by('user_type')
    return render(request,'administration/manage/manage_users.html',{
        'users':users,
    })

@login_required()
def approve_user(request,id):
    user = User.objects.get(pk=id)
    user.approved = 'Yes'
    user.save()

    # Prepare account activation email
    current_site = get_current_site(request)
    protocol = request.scheme  # Detect 'http' or 'https'
    email_subject = 'Tutor King Account Approval'
    message = render_to_string('administration/account_approval_email.html', {
        'user': user,
        'domain': current_site.domain,
        'protocol': protocol,
        
    })
    to_email = user.email
    email = EmailMessage(email_subject, message, to=[to_email])

    try:
        email.send()
        messages.success(request, 'Account approved successfully.')
        return redirect('manage-users')
    except Exception as e:
        # Fallback if email fails
        messages.error(request, f'Email could not be sent: {e}')
        return redirect('manage-users')



@login_required()
def disapprove_user(request,id):
    user = User.objects.get(pk=id)
    user.approved = 'No'
    user.save()

    # Prepare account activation email
    current_site = get_current_site(request)
    protocol = request.scheme  # Detect 'http' or 'https'
    email_subject = 'Tutor King Account Approval'
    message = render_to_string('administration/account_dissapproval_email.html', {
        'user': user,
        'domain': current_site.domain,
        'protocol': protocol,
        
    })
    to_email = user.email
    email = EmailMessage(email_subject, message, to=[to_email])

    try:
        email.send()
        messages.success(request, 'Account approved successfully.')
        return redirect('manage-users')
    except Exception as e:
        # Fallback if email fails
        messages.error(request, f'Email could not be sent: {e}')
        return redirect('manage-users')

@login_required()
def delete_user(request,id):
    user = User.objects.get(pk=id)
    user.delete()
    messages.error(request, 'User account deleted successfully.')
    return redirect('manage-users')

def manage_tutors_view(request):
    tutors = User.objects.filter(user_type='Tutor')
    return render(request, 'administration/manage/manage_tutors.html', {
        'tutors': tutors,
    })

@login_required()
def manage_subjects_view(request):
    subjects = Subject.objects.all()
    return render(request, 'administration/manage/manage_subjects.html', {
        'subjects': subjects
    })

@login_required()
def add_learner_view(request):
    if request.method == 'POST':
        form = LearnerForm(request.POST)
        if form.is_valid():
            learner = form.save(commit=False)
            learner.save()
            messages.success(request, 'Learner added successfully.')
            return redirect('manage-learners')
        else:
            messages.error(request, 'Error adding learner. Please check the form.')
    else:
        form = LearnerForm()
    
    return render(request, 'administration/forms/add_learner.html', {
        'form': form
    })
@login_required()
def update_learner_view(request, id):
    learner = Learner.objects.get(pk=id)
    if request.method == 'POST':
        form = LearnerForm(request.POST, instance=learner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Learner updated successfully.')
            return redirect('manage-learners')
        else:
            messages.error(request, 'Error updating learner. Please check the form.')
    else:
        form = LearnerForm(instance=learner)
    
    return render(request, 'administration/forms/update_learner.html', {
        'form': form
    })
@login_required()
def delete_learner_view(request, id):
    learner = Learner.objects.get(pk=id)
    learner.delete()
    messages.success(request, 'Learner deleted successfully.')
    return redirect('manage-learners')
@login_required()
def manage_learners_view(request):
    learners = Learner.objects.all()
    return render(request, 'administration/manage/manage_learners.html', {
        'learners': learners
    })

@login_required()
def manage_classes_view(request):
    classes = Class.objects.all()
    return render(request, 'administration/manage/manage_classes.html', {
        'classes': classes
    })

@login_required()
@login_required()
def manage_class_learners_view(request, id):  
    class_instance = get_object_or_404(Class, id=id, tutor=request.user)
    class_learners = ClassLearners.objects.filter(class_instance=class_instance).all()
    return render(request, 'administration/manage/manage_class_learners.html', {
        'learners': class_learners,
        'class': class_instance
    })

def manage_tutor_payments_view(request):
    tutors = User.objects.filter(user_type='Tutor')
    payments = Payment.objects.all()

    tutor_payment_data = []
    for tutor in tutors:
        total_amount = 0
        tutors_full_name = tutor.get_full_name().strip().lower()
        first_name = tutor.first_name.strip().lower()
        last_name = tutor.last_name.strip().lower()

        for payment in payments:
            payment_tutor_name = payment.tutors_full_name.strip().lower()
            payment_referrer_name = payment.referrers_full_name.strip().lower()

            # Match if payment name contains either first or last name
            if (
                tutors_full_name in payment_tutor_name
                or first_name in payment_tutor_name
                or last_name in payment_tutor_name
            ):
                total_amount += payment.amount_due_to_tutor

            elif (
                tutors_full_name in payment_referrer_name
                or first_name in payment_referrer_name
                or last_name in payment_referrer_name
            ):
                total_amount += payment.amount_due_to_referrer

        tutor_payment_data.append({
            'tutor_name': tutor.get_full_name().title(),  # keep original case for display
            'total_payment': total_amount
        })

    return render(request, 'administration/manage/manage_tutor_payments.html', {
        'tutor_payment_data': tutor_payment_data
    })

@login_required
def upload_past_paper(request):
    if request.method == 'POST':
        form = PastQuestionPaperForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Past paper uploaded successfully.")
            return redirect('administrator')
    else:
        form = PastQuestionPaperForm()

    return render(request, 'administration/forms/upload_past_question_paper.html', {'form': form})
