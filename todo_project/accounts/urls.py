from django.urls import path
from . import views 
from django.contrib.auth.views import(
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView)
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name ='accounts/password_reset.html'
    email_template_name='accounts/password_reset_email.html'
    subject_template_name='accounts/password_reset_subject'
    success_message= "We've emailed you the instructions for setting your password,"\
        "if an account exists with the email you entered. You should recieve them shortly."\
        "If you don't recieve an email,"\
            "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('user/accounts/login')



urlpatterns = [
    # login, logout, register
    path('login/',views.loginUser, name='login'), 
    path('register/',views.registerUser, name='register'), 
    path('logout/',views.logoutUser, name='logout'), 

    # edit username, email, password
    path('user-profile/edit/username_or_email/',views.editUserNameOrEmail, name='editUserNameOrEmail'), 
    path('user-profile/edit/password/', views.editUserNameOrEmail, name='editUserPassword'),

    # password reset
    path('password/reset/form/', views.passwordResetForm, name='passwordResetForm'),
    path('password/reset/form/<str:uid>/<str:token>/', views.passwordResetConfirm, name='passwordResetConfirm'),
]
