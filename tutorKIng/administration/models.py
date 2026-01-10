from django.db import models

from tutor.models import Subject
# Create your models here.

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


class Learner(models.Model):
    learner = models.OneToOneField('authentication.User', on_delete=models.CASCADE)
    tutor1 = models.ForeignKey('authentication.User', related_name='tutor1', on_delete=models.DO_NOTHING)
    tutor2 = models.ForeignKey('authentication.User', related_name='tutor2', on_delete=models.DO_NOTHING, null=True, blank=True)
    tutor3 = models.ForeignKey('authentication.User', related_name='tutor3', on_delete=models.DO_NOTHING, null=True, blank=True)
    grade = models.CharField(max_length=50, choices=GRADE_CHOICES)
    subject1 = models.ForeignKey('tutor.Subject', related_name='subject1', on_delete=models.DO_NOTHING)
    subject2 = models.ForeignKey('tutor.Subject', related_name='subject2', on_delete=models.DO_NOTHING, null=True, blank=True)
    subject3 = models.ForeignKey('tutor.Subject', related_name='subject3', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f"Learner: {self.learner.first_name} {self.learner.last_name}"

def past_paper_upload_path(instance, filename):
    paper = f"paper_{instance.paper_number}" if instance.paper_number else "general"

    subject_name = instance.subject.name.lower().replace(' ', '_')
    grade = instance.subject.grade.lower().replace(' ', '_')

    return (
        f"past_papers/"
        f"{grade}/"
        f"{subject_name}/"
        f"{instance.year}/"
        f"{paper}/"
        f"{filename}"
    )

class PastQuestionPaper(models.Model):
    PAPER_CHOICES = [
        ('', '----Select----'),
        (1, "Paper 1"),
        (2, "Paper 2"),
        (3, "Paper 3"),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='past_papers'
    )

    year = models.PositiveIntegerField()

    paper_number = models.PositiveSmallIntegerField(
        choices=PAPER_CHOICES,
        blank=True,
        null=True
    )

    question_file = models.FileField(upload_to=past_paper_upload_path)
    memo_file = models.FileField(upload_to=past_paper_upload_path)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        paper = f"Paper {self.paper_number}" if self.paper_number else "General"
        return (
            f"{self.subject.name} | "
            f"{self.subject.grade} | "
            f"{self.year} | {paper}"
        )
