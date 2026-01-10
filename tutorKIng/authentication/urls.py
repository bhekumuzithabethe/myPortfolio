from django.urls import path
from . import views
urlpatterns = [
    path('', views.home_view, name='home'),
    # path('accounts/tutor-sign-up/',views.tutor_account_registration_view, name='tutor-sign-up'),
    # path('accounts/sign-up/',views.learner_account_registration_view, name='learner-sign-up'),
    path("sign-up/<str:role>/", views.account_registration_view, name="signup"),

    path('accounts/account-activation/<str:uidb64>/<str:token>/', views.account_activation_view, name='account-activation'),
    path('dologin/', views.login_view, name='dologin'),
    path('logout/', views.logout_view, name='dologout'),
    path('pending-approval/', views.account_pending_approval, name='pending-approval'),

    path('update-profile/', views.update_user_profile, name='update-profile'),
]
