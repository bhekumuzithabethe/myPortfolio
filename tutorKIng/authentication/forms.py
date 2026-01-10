from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [ 'email', 'password1', 'password2']
        labels = {
            'email': 'Email address',
            'password1': 'Password',
            'password2': 'Confirm password',
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    # Exclude show_password from the cleaned data since it's not a model field
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.pop('show_password', None)
        return cleaned_data

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_pic']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

   