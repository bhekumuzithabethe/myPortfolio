from django import forms
from .models import Learner, PastQuestionPaper
from authentication.models import User
from tutor.models import Subject
class LearnerForm(forms.ModelForm):

    class Meta:
        model = Learner
        fields = ("learner", "tutor1", "tutor2", "tutor3", "grade", "subject1", "subject2", "subject3")
    
    def __init__(self, *args, **kwargs):
        super(LearnerForm, self).__init__(*args, **kwargs)
        self.fields['learner'].empty_label = '-- Select --'
        self.fields['tutor1'].empty_label = '-- Select --'
        self.fields['tutor2'].empty_label = '-- Select --'
        self.fields['tutor3'].empty_label = '-- Select --'
        self.fields['subject1'].empty_label = '-- Select --'
        self.fields['subject2'].empty_label = '-- Select --'
        self.fields['subject3'].empty_label = '-- Select --'

        self.fields['learner'].queryset = User.objects.filter(user_type='Learner')
        # Tutors
        tutor_queryset = User.objects.filter(user_type='Tutor')
        self.fields['tutor1'].queryset = tutor_queryset
        self.fields['tutor2'].queryset = tutor_queryset
        self.fields['tutor3'].queryset = tutor_queryset
        #Subjects
        subject_queryset = Subject.objects.all()
        self.fields['subject1'].queryset = subject_queryset
        self.fields['subject2'].queryset = subject_queryset
        self.fields['subject3'].queryset = subject_queryset

class PastQuestionPaperForm(forms.ModelForm):
    class Meta:
        model = PastQuestionPaper
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PastQuestionPaperForm,self).__init__(*args, **kwargs)
        subject_queryset = Subject.objects.all()
        self.fields['subject'].empty_label = '-- Select --'
        self.fields['subject'].queryset = subject_queryset
