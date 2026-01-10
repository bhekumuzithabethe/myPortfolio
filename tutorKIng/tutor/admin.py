from django.contrib import admin
from .models import Month, Payment, Client, Quiz, Question, Answer,Subject, ClassLearners, Class

# Register your models here.
admin.site.register(Month)
admin.site.register(Payment)
admin.site.register(Client)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Subject)
admin.site.register(ClassLearners)
admin.site.register(Class)

