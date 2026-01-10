from django.contrib import admin
from .models import QuizAttempt,UserAnswer
# Register your models here.
admin.site.register(QuizAttempt)
admin.site.register(UserAnswer)