from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
USER_TYPE_CHOICES = (
    ('','Select'),
    ('Admin','Admin'),
    ('Tutor','Tutor'),
    ('Learner','Learner'),
)

# Create your models here.
class User(AbstractUser):
    user_type = models.CharField(max_length=10,choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to='profile pictures',null=True,blank=True)
    approved = models.CharField(max_length=4,default='No')
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'