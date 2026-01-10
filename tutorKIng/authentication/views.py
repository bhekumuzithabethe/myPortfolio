# Django imports for views and helpers
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, UpdateUserForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import User
# =============================
# Home Page View
# =============================
def home_view(request):
    # Retrieve any stored messages to display in the template (success/errors)
    messages_to_display = messages.get_messages(request)
    return render(request, 'registration/base.html', {
        'messages': messages_to_display,
    })

# =============================
# User Registration View
# =============================
def account_registration_view(request, role):
    if role not in ["tutor", "learner"]:
        return redirect("home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            # Duplicate checks
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
            elif password1 != password2:
                messages.error(request, "Passwords do not match.")
            else:
                user = form.save(commit=False)

                # CRITICAL FIX
                user.username = email

                user.email = email
                user.is_active = False
                user.user_type = role.title()
                user.save()

                # Email activation
                try:
                    current_site = get_current_site(request)
                    protocol = request.scheme
                    message = render_to_string(
                        'registration/account_activation_email.html',
                        {
                            'user': user,
                            'domain': current_site.domain,
                            'protocol': protocol,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        }
                    )

                    EmailMessage(
                        "Activate your account",
                        message,
                        to=[email]
                    ).send()

                    messages.success(
                        request,
                        "Check your email to activate your account."
                    )
                    return redirect("home")

                except Exception as e:
                    messages.error(request, f"Email could not be sent: {e}")

    else:
        form = RegistrationForm()

    return render(
        request,
        "registration/sign_up.html",
        {"form": form, "role": role}
    )
  
# =============================
# Account Activation View
# =============================
def account_activation_view(request, uidb64, token):
    User = get_user_model()
    try:
        # Decode the UID from the activation URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None

    # Validate token and activate account
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        authenticate(username=user.username, password=user.password)
        login(request, user)
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('update-profile')
    else:
        messages.error(request, 'Your activation link is invalid or expired.')
        return redirect('home')


# =============================
# Login View
# =============================
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user and user.is_active:
                login(request, user, backend='authentication.backends.EmailBackend')

                if user.user_type == 'Admin':
                    return redirect('administrator')
                elif user.user_type == 'Tutor' and user.approved == 'Yes':
                    return redirect('tutor')
                elif user.user_type == 'Learner' and user.approved == 'Yes':
                    return redirect('learner')
                elif user.user_type in ['Tutor', 'Learner'] and user.approved == 'No':
                    return redirect('pending-approval')
                else:
                    messages.error(request, "Unauthorized user type.")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {'form': form})

# =============================
# Logout View
# =============================
@login_required  # Ensures only logged-in users can access logout
def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to homepage after logout

def account_pending_approval(request):
    return render(request, 'index.html',{
    })

@login_required  # Ensures only logged-in users can access logout
def update_user_profile(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            user= request.user
            messages.success(request, 'Profile updated successfully.')
            if user.user_type == "Learner" and user.approved == 'Yes':
                return redirect('learner')
            elif user.user_type == "Tutor" and user.approved == 'Yes':
                return redirect('tutor')
            elif user.user_type == "Admin":
                return redirect('administrator')
            elif user.approved == 'No':
                return redirect('pending-approval')
        else:
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = UpdateUserForm(instance=request.user)
        user = request.user 

        if user.user_type == "Learner" and user.approved == 'Yes':
            base_template = "learner/index.html"
        elif user.user_type == "Tutor" and user.approved == 'Yes':
            base_template = "tutor/index.html"
        elif user.user_type == "Admin":
            base_template = "administration/index.html"
        else:
            base_template = "index.html"  
        home_url = ''

        user = request.user
        if user.user_type == "Learner" and user.approved == 'Yes':
            home_url = 'learner'
        elif user.user_type == "Tutor" and user.approved == 'Yes':
            home_url = 'tutor'
        elif user.user_type == "Admin":
            home_url = 'administrator'
    return render(request, 'registration/update_profile.html', {
        'form': form,
        'base_template': base_template,
        'home_url': home_url,
    })

