from django.db import models
from django.db.models import Max
from datetime import datetime 
import uuid
import os
# Create your models here.
  
SUBSCRIPTION_CHOICES = [
    ('', '----Select----'),
    ('Online Tutoring', 'Online Tutoring'),
    ('Sporadic Tutoring', 'Sporadic Tutoring'),
    ('Online Video Lessons', 'Online Video Lessons')
]  


CLIENT_STATED_CHOICES= [
    ('', '----Select----'),
    ('1st Month', '1st Month'),
    ('2st Month', '2st Month'),
    ('3rd Month', '3rd Month'),
    ('4th Month', '4th Month'),
    ('5th Month', '5st Month'),
    ('6th Month', '6th Month'),
    ('7th Month', '7th Month'),
    ('8th Month', '8th Month'),
    ('9th Month', '9th Month'),
    ('10th Month', '10th Month'),
    ('11th Month', '11th Month'),
    ('12th Month', '12th Month'),
]


GRADE_CHOICES = [
    ('', '----Select----'),
    ('Grade 1', 'Grade 1'),
    ('Grade 2', 'Grade 2'),
    ('Grade 3', 'Grade 3'),
    ('Grade 4', 'Grade 4'),
    ('Grade 5', 'Grade 5'),
    ('Grade 6', 'Grade 6'),
    ('Grade 7', 'Grade 7'),
    ('Grade 8', 'Grade 8'),
    ('Grade 9', 'Grade 9'),
    ('Grade 10', 'Grade 10'),
    ('Grade 11', 'Grade 11'),
    ('Grade 12', 'Grade 12'),
    
]

MONTH_CHOICES = [
    ('', '----Select----'),
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]

PAYMENT_PERCENTAGES = [
    ('', '----Select----'),
    ('Split Of 70%  Total', 'Split Of 70%  Total'),
    ('Remainder After Referrer Fee', 'Remainder After Referrer Fee'),
    ('Slit Of Remainder After Referrer Fee', 'Slit Of Remainder After Referrer Fee'),

]

REFEER_PAYMENT_PERCENTAGES = [
    ('', '----Select----'),
    ('20% of Tutors total', '20% of Tutors total'),
    ('100% of total', '100% of total'),
    ('Slit Of Remainder After Referrer Fee', 'Slit Of Remainder After Referrer Fee'),

]
CLIENT_STATUS = [
    ('', '----Select----'),
    ('Started', 'Started'),
    ('Start next month/future', 'Start next month/future'),

]
YES_OR_NO = [
    ('', '----Select----'),
    ('YES', 'YES'),
    ('NO', 'NO'),
 
]
class Month(models.Model):
    current_month = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'Month: {self.current_month}'


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("proof_of_payments/", new_filename)

class Payment(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    tutors_full_name = models.CharField(max_length=50)
    referrers_full_name = models.CharField(max_length=50)
    parents_full_name = models.CharField(max_length=50)
    learners_full_name = models.CharField(max_length=50)
    grade_of_learner = models.CharField(max_length=50,choices=GRADE_CHOICES)
    leaners_subjects = models.CharField(max_length=50)
    total_number_of_days_learner_does_per_week = models.IntegerField(blank=True,null=True)
    number_of_days_you_tutor_per_week = models.IntegerField(blank=True,null=True)
    name_of_2nd_tutor = models.CharField(max_length=50, null=True,blank=True)
    name_of_3rd_tutor = models.CharField(max_length=50, null=True,blank=True)
    date_of_payment = models.DateTimeField()
    proof_of_payment = models.FileField(upload_to=upload_to, max_length=100)
    type_of_subscription = models.CharField(max_length=50,choices=SUBSCRIPTION_CHOICES)
    cost_of_subscription = models.FloatField()
    month_as_active_client = models.CharField(max_length=50,choices=CLIENT_STATED_CHOICES)
    amount_due_to_referrer = models.FloatField()
    amount_due_to_tutor = models.FloatField(blank=True,null=True,default=0)

    def __str__(self):
        return f"{self.name_of_learner} - {self.month}"

class Client(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    tutors_full_name = models.CharField(max_length=50)
    parents_full_name = models.CharField(max_length=50)
    learners_full_name = models.CharField(max_length=50)
    month_client_started = models.CharField( max_length=50, choices=MONTH_CHOICES)
    referrers_name = models.CharField(max_length=50)
    grade_of_learner = models.CharField( max_length=50, choices=GRADE_CHOICES)
    subjects_you_tutor = models.TextField()
    number_of_days_you_tutor = models.IntegerField()
    percentage_of_payment_you_are_due = models.CharField(max_length=50,choices=PAYMENT_PERCENTAGES)
    name_of_2nd_tutor = models.CharField(max_length=50, null=True, blank=True)
    subjects_of_2nd_tutor = models.CharField(max_length=50, null=True, blank=True)
    name_of_3rd_tutor = models.CharField(max_length=50, null=True, blank=True)
    subjects_of_3rd_tutor = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=CLIENT_STATUS)
    date_learner_started_or_due_to_start = models.DateTimeField()
    did_client_pay_this_month = models.CharField(max_length=50, blank=True, null=True, choices=YES_OR_NO)
    filled_in_payments_form = models.CharField(max_length=50, blank=True, null=True, choices=YES_OR_NO)
    did_you_get_payed_this_month = models.CharField(max_length=50, blank=True, null=True, choices=YES_OR_NO)
    amount_client_paid = models.FloatField()

    def __str__(self):
        return f'Client: {self.parent_full_name} - Learner: {self.learners_full_name} - Month: {self.month}'

class Referrer(models.Model):
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    referrers_name = models.CharField(max_length=50)
    parents_full_name = models.CharField(max_length=50)
    learners_full_name = models.CharField(max_length=50)
    month_client_started = models.CharField( max_length=50, choices=MONTH_CHOICES)
    grade_of_learner = models.CharField( max_length=50, choices=GRADE_CHOICES)
    tutors_full_name = models.CharField(max_length=50)
    subjects_tutor_does = models.TextField()
    number_of_days_they_tutor = models.IntegerField()
    percentage_of_payment_you_are_due = models.CharField(max_length=50,choices=REFEER_PAYMENT_PERCENTAGES)
    name_of_2nd_tutor = models.CharField(max_length=50, null=True, blank=True)
    subjects_of_2nd_tutor = models.CharField(max_length=50, null=True, blank=True)
    name_of_3rd_tutor = models.CharField(max_length=50, null=True, blank=True)
    subjects_of_3rd_tutor = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, choices=CLIENT_STATUS)
    date_learner_started_or_due_to_start = models.DateTimeField()
    did_client_pay_this_month = models.CharField( blank=True, null=True, choices=YES_OR_NO)
    filled_in_payments_form = models.CharField( blank=True, null=True, choices=YES_OR_NO)
    did_you_get_payed_this_month = models.CharField( blank=True, null=True, choices=YES_OR_NO)
    amount_client_paid = models.FloatField()

    def __str__(self):
        return f'Referrer: {self.referrers_name} - Learner: {self.learners_full_name} - Month: {self.month}'


class Subject(models.Model):
    tutor = models.ForeignKey('authentication.User', on_delete=models.DO_NOTHING, related_name='subjects')
    name = models.CharField(max_length=100)
    grade = models.CharField(max_length=50, choices=GRADE_CHOICES)
    def __str__(self):
        return f'Subject: {self.name} - Grade: {self.grade} - Tutor: {self.tutor.first_name} {self.tutor.last_name}'

   
UNDERSTANDING_CHOICES = [
    ('', '----Select----'),
    ('Does not understand', 'Does not understand'),
    ('Extra Lesson', 'Extra Lesson'),
    ('Extra activity','Extra activity'),
    ('Confident in the topic','Confident in the topic'),

] 
  
QUESTION_TYPE = (
    ('', ('--Select--')),
    (1, ('Multiple Choice')),
    (2, ('True or False')),
    (3, ('Text Answer from learner')),
    (4, ('Paragraph Answer from learner '))
    )
class Quiz(models.Model):
    class Meta:
        verbose_name = ("Quiz")
        verbose_name_plural = ("Quizzes")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    quiz_title = models.CharField(max_length=255, verbose_name=("Quiz Title"), unique=True)
    total_marks = models.IntegerField(default=0)
    duration = models.IntegerField(help_text="Quiz duration in minutes")
    date_created = models.DateTimeField(verbose_name=("Date Created"),default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True, verbose_name=("Date Updated")) 
     
    def __str__(self):
        return f'Quiz : {self.quiz_title}'

# class Question(models.Model):
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,related_name='question_set')
#     question_type = models.IntegerField(choices=QUESTION_TYPE, default=0, verbose_name=("Type of Questions"))
#     question_number = models.IntegerField(default=1, verbose_name=("Question Number"))
#     question = models.CharField(max_length=255, verbose_name=("Question"))
#     mark = models.IntegerField()
#     date_created = models.DateTimeField(verbose_name=("Date Created"),default=datetime.now)
#     date_updated = models.DateTimeField(auto_now=True, verbose_name=("Date Updated")) 
    
#     # def get_answers(self):
#     #     return self.answer_set.all()
#     def __str__(self):
#         return f'{self.question_number}'



class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='question_set')
    question_type = models.IntegerField(choices=QUESTION_TYPE, default=0, verbose_name=("Type of Questions"))
    question_number = models.IntegerField(default=0, verbose_name=("Question Number"))  # Change default to 0
    question = models.CharField(max_length=255, verbose_name=("Question"))
    mark = models.IntegerField()
    date_created = models.DateTimeField(verbose_name=("Date Created"), default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True, verbose_name=("Date Updated"))
    
    def save(self, *args, **kwargs):
        # Only auto-increment if this is a new question (no ID yet)
        if not self.pk:
            # Get the maximum question_number for this quiz
            max_number = Question.objects.filter(quiz=self.quiz).aggregate(
                Max('question_number')
            )['question_number__max']
            
            # If no questions exist yet, start from 1
            if max_number is None:
                self.question_number = 1
            else:
                self.question_number = max_number + 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.question_number}'

class Answer(models.Model):
    class Meta:
        verbose_name = ("Answer")
        verbose_name_plural = ("Answers")

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_set')
    answer = models.CharField(max_length=255, verbose_name=("Answer"))
    is_right = models.BooleanField(default=False,blank=True)
    date_created = models.DateTimeField(verbose_name=("Date Created"),default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True, verbose_name=("Date Updated")) 
    
    def __str__(self):
        return f'{self.answer}'

class Class(models.Model):
    class_name = models.CharField(max_length=100, unique=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    grade = models.CharField(max_length=50, choices=GRADE_CHOICES)
    tutor = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='tutors_classes')
    google_meet_link = models.CharField(max_length=200, blank=True, null=True)
    lesson_time = models.TimeField(blank=True, null=True)
    lesson_days = models.TextField(blank=True, null=True, help_text="Enter days of the week separated by commas (e.g., Monday, Wednesday, Friday)")
    
    class Meta:
        verbose_name = ("Class")
        verbose_name_plural = ("Classes")

    def __str__(self):
        return f'Class: {self.class_name} - Subject: {self.subject.name} - Tutor: {self.tutor.first_name} {self.tutor.last_name}'

class ClassLearners(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_learners', default=None)
    learner_1 = models.ForeignKey('administration.Learner', on_delete=models.DO_NOTHING, related_name='class_learner_1', blank=True, null=True)
    learner_2 = models.ForeignKey('administration.Learner', on_delete=models.DO_NOTHING, related_name='class_learner_2', blank=True, null=True)
    learner_3 = models.ForeignKey('administration.Learner', on_delete=models.DO_NOTHING, related_name='class_learner_3', blank=True, null=True)
    learner_4 = models.ForeignKey('administration.Learner', on_delete=models.DO_NOTHING, related_name='class_learner_4', blank=True, null=True)
    learner_5 = models.ForeignKey('administration.Learner', on_delete=models.DO_NOTHING, related_name='class_learner_5', blank=True, null=True)

    class Meta:
        verbose_name = ("Class Learner")
        verbose_name_plural = ("Class Learners")

    def __str__(self):
        return f' Class: {self.class_name.class_name}'
