# models.py - Add these models
from django.db import models
from authentication.models import User
from django.utils import timezone
from tutor.models import Question, Quiz

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'quiz']
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_title}"
    
    def calculate_score(self):
        """Calculate total score from user answers"""
        user_answers = self.useranswer_set.all()
        total = 0
        for ua in user_answers:
            if ua.is_correct:
                total += ua.question.mark
        self.total_score = total
        self.save()
        return total

class UserAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    answered_at = models.DateTimeField(default=timezone.now)
    needs_marking = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marked_answers')
    marked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['quiz_attempt', 'question']
        verbose_name = "User Answer"
        verbose_name_plural = "User Answers"
    
    def __str__(self):
        return f"{self.quiz_attempt.user.username} - Q{self.question.question_number}"
    
    def auto_mark(self):
        """Automatically mark the answer if possible"""
        if self.question.question_type in [1, 2]:  # Multiple Choice or True/False
            if self.question.question_type == 1:
                # Multiple Choice
                try:
                    answer_id = int(self.user_answer)
                    correct_answer = self.question.answer_set.filter(is_right=True).first()
                    if correct_answer and answer_id == correct_answer.id:
                        self.is_correct = True
                        self.marks_awarded = self.question.mark
                    else:
                        self.is_correct = False
                        self.marks_awarded = 0
                except (ValueError, TypeError):
                    self.is_correct = False
                    self.marks_awarded = 0
            elif self.question.question_type == 2:
                # True/False
                correct_answer = self.question.answer_set.filter(is_right=True).first()
                if correct_answer and self.user_answer == correct_answer.answer:
                    self.is_correct = True
                    self.marks_awarded = self.question.mark
                else:
                    self.is_correct = False
                    self.marks_awarded = 0
            
            self.needs_marking = False
            self.save()
            return True
        
        # Text answers need manual marking
        elif self.question.question_type in [3, 4]:
            self.needs_marking = True
            self.save()
            return False
        
        return False