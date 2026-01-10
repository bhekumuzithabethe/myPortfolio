from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Payment, Client, Quiz,Question,Answer, Subject, Referrer, Class, ClassLearners
from django.forms import BaseInlineFormSet, inlineformset_factory

class ClientForm(forms.ModelForm):
    date_learner_started_or_due_to_start = forms.DateField(label="From Date", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Client
        fields = ['tutors_full_name','parents_full_name','learners_full_name','month_client_started','referrers_name','grade_of_learner','subjects_you_tutor','number_of_days_you_tutor','percentage_of_payment_you_are_due','name_of_2nd_tutor','subjects_of_2nd_tutor','name_of_3rd_tutor','subjects_of_3rd_tutor','status','date_learner_started_or_due_to_start','did_client_pay_this_month','filled_in_payments_form','did_you_get_payed_this_month','amount_client_paid']
        widgets={
            'date_learner_started_or_due_to_start': forms.DateInput(format='%Y-%m-%d'),
        }

class ReferrerForm(forms.ModelForm):
    date_learner_started_or_due_to_start = forms.DateField(label="From Date", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Referrer
        fields = ['tutors_full_name','parents_full_name','learners_full_name','month_client_started','grade_of_learner','subjects_tutor_does','number_of_days_they_tutor','percentage_of_payment_you_are_due','name_of_2nd_tutor','subjects_of_2nd_tutor','name_of_3rd_tutor','subjects_of_3rd_tutor','status','date_learner_started_or_due_to_start','did_client_pay_this_month','filled_in_payments_form','did_you_get_payed_this_month','amount_client_paid']
        widgets={
            'date_learner_started_or_due_to_start': forms.DateInput(format='%Y-%m-%d'),
        }

# Set up allowed and disallowed file types
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'pdf', 'txt']
ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'application/pdf', 'text/plain']
DANGEROUS_EXTENSIONS = ['exe', 'php', 'sh', 'js', 'bat']

MAX_FILE_SIZE_MB = 5

def validate_file_size(file):
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'Max file size is {MAX_FILE_SIZE_MB}MB')

class PaymentForm(forms.ModelForm):
    date_of_payment = forms.DateField(label="Payment Date", widget=forms.DateInput(attrs={'type': 'date'}))
    proof_of_payment = forms.FileField(
        help_text="Upload a JPG, PNG, or PDF (max 5MB).",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'pdf'])]
        )

    class Meta:
        model = Payment
        fields = [
            'referrers_full_name', 'parents_full_name',
            'learners_full_name', 'grade_of_learner', 'leaners_subjects','total_number_of_days_learner_does_per_week',
            'number_of_days_you_tutor_per_week','name_of_2nd_tutor', 'name_of_3rd_tutor', 'date_of_payment',
            'proof_of_payment', 'type_of_subscription', 'cost_of_subscription',
            'month_as_active_client'
        ]
        exclude = ['tutors_full_name']

    def clean_proof_of_payment(self):
        file = self.cleaned_data['proof_of_payment']
        validate_file_size(file)
        return file


class DateInput(forms.DateInput):
    input_type = 'date'

class QuizForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Quiz
        fields = ('subject','quiz_title','duration','total_marks')
        widgets ={
            'due_date':DateInput(attrs={'class': 'form-control'}),            
        }
    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)  # extract tutor from kwargs
        super(QuizForm, self).__init__(*args, **kwargs)
        self.fields['subject'].empty_label = '--Select--'

        if tutor:
            self.fields['subject'].queryset = Subject.objects.filter(tutor=tutor).all()
        else:
            self.fields['subject'].queryset = Subject.objects.none()

    

# class QuestionForm(forms.ModelForm):
#     QUESTION_TYPE = (
#     ('', ('--Select--')),
#     (1, ('Multiple Choice')),
#     (2, ('True or False')),
#     (3, ('Text Answer from learner')),
#     (4, ('Paragraph Answer from learner '))
#     )
#     question_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),choices=QUESTION_TYPE)
#     class Meta:
#         model = Question
#         fields = ['question_type','question_number','question','mark']

class QuestionForm(forms.ModelForm):
    QUESTION_TYPE = (
        ('', ('--Select--')),
        (1, ('Multiple Choice')),
        (2, ('True or False')),
        (3, ('Paragraph Answer from learner '))
    )
    question_type = forms.ChoiceField(
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_question_type',
            'onchange': 'toggleAnswerFields()'
        }),
        choices=QUESTION_TYPE
    )
    
    class Meta:
        model = Question
        fields = ['question_type', 'question', 'mark']  # Remove question_number from form
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),
            'mark': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove question_number field from form since it's auto-generated
        if 'question_number' in self.fields:
            del self.fields['question_number']


class CustomAnswerFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially hide all forms
        for form in self.forms:
            form.fields['answer'].widget.attrs.update({'class': 'answer-field'})
            form.fields['is_right'].widget.attrs.update({'class': 'is-right-field'})

AnswerFormSet = inlineformset_factory(
    Question, Answer,
    formset=CustomAnswerFormSet,
    fields=['answer', 'is_right'],
    extra=4,
    can_delete=False
)


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'grade']
    
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Subject Name"

class TimeInput(forms.DateInput):
    input_type = 'time'

    def __init__(self, attrs=None, format='%H:%M'):
        super().__init__(attrs=attrs, format=format)

class ClassForm(forms.ModelForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Class
        fields = ("class_name", "subject", "grade", "lesson_time", "lesson_days","google_meet_link")
        widgets = {
            'lesson_time': TimeInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)  # extract tutor from kwargs
        super(ClassForm, self).__init__(*args, **kwargs)
        self.fields['subject'].empty_label = '--Select--'

        if tutor:
            self.fields['subject'].queryset = Subject.objects.filter(tutor=tutor).all()
        else:
            self.fields['subject'].queryset = Subject.objects.none()

class ClassLearnersForm(forms.ModelForm):
    class_name = forms.ModelChoiceField(
        queryset=ClassLearners.objects.none(), 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = ClassLearners
        fields = ("class_name", "learner_1", "learner_2", "learner_3", "learner_4", "learner_5")

    def __init__(self, *args, **kwargs):
        tutor = kwargs.pop('tutor', None)  # extract tutor from kwargs
        super(ClassLearnersForm, self).__init__(*args, **kwargs)
        self.fields['class_name'].empty_label = '--Select--'
        self.fields['learner_1'].empty_label = '--Select--'
        self.fields['learner_2'].empty_label = '--Select--'
        self.fields['learner_3'].empty_label = '--Select--'
        self.fields['learner_4'].empty_label = '--Select--'
        self.fields['learner_5'].empty_label = '--Select--'

        if tutor:
            self.fields['class_name'].queryset = Class.objects.filter(tutor=tutor).all()
        else:

            self.fields['class_name'].queryset = Class.objects.none()
