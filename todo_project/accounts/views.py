from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import registrationForm
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from . import views

def registerUser(request):
    page = 'register'
    if request.user.is_authenticated:
        return redirect('viewTasks')

    registration_form = registrationForm()

    if request.method == 'POST':
        registration_form = registrationForm(request.POST)
        if registration_form.is_valid():
            new_user = registration_form.save(commit=False)
            new_user.username = new_user.username.lower()
            new_user.save()
            login(request, new_user)
            subject = 'Todo App: Thank you for Registering'
            message = f'Hi {new_user.username}, thanks for signing up, hope you will enjoy using this app.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [new_user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            return redirect('viewTasks')
        else:
            messages.error(request, 'ERROR: The user form was not valid. Failed to create a new user')
    else:
        pass

    context = {'page': page, 'registrationForm': registration_form}
    return render(request, 'accounts/userRegistration.html', context)

def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('viewTasks')

    if request.method == 'POST':
        username_or_email = request.POST['username_or_email'].lower()
        password = request.POST['password1']

        try:
            user = User.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email))
            db_user = authenticate(
                request, username=user.username, password=password)
            
            if db_user is not None:
                login(request, db_user)
                subject = 'Todo App: Someone logged into your account'
                message = f'Hi {request.user.username}, \n You have successfully logged into your account.'
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [request.user.email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=True)
                return redirect('viewTasks')
            else:
                messages.error(
                    request, "ERROR: invalid username or password, please check the login details and try again.")
        except User.DoesNotExist:
            messages.error(
                request, "ERROR: invalid login credentials, please try again.")
    context = {'page': page}
    return render(request, 'accounts/userLogin.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def editUserNameOrEmail(request):
    page = 'editUserNameOrEmail'
    userProfile = request.user
    if request.method == 'POST':
        change_username = request.POST['change_username']
        change_email = request.POST['change_email']
        user_password = request.POST['password']

        correctUserPassword = authenticate(request, username=userProfile.username, password=user_password)

        if correctUserPassword:
            if change_username:
                username_already_exists = User.objects.filter(username=change_username)
                if not username_already_exists:
                    old_username = request.user.username
                    userProfile.username = change_username
                    messages.success(request, f'Username changed from "{old_username}" to "{change_username}"')
                else:
                    messages.error(request, f'ERROR: The username "{change_username}" already exists. Please choose a different username.')

            if change_email:
                email_already_exists = User.objects.filter(email=change_email)
                if not email_already_exists:
                    old_email = request.user.email
                    userProfile.email = change_email
                    messages.success(request, f'Email changed from "{old_email}" to "{change_email}"')
                else:
                    messages.error(request, f'ERROR: The email "{change_email}" already exists. Please choose a different email.')

            userProfile.save()

    context = {'page': page}
    return render(request, 'accounts/editUserNameOrEmail.html', context)

def passwordResetForm(request):
    page = 'passwordResetForm'

    if request.user.is_authenticated:
        return redirect('viewTasks')

    if request.method == 'POST':
        reset_email = request.POST['reset_email']

        user_with_email_exists = User.objects.filter(email=reset_email)

        if user_with_email_exists:
            user = user_with_email_exists.first()
            uid = str(user.id)
            token = default_token_generator.make_token(user)
            password_reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')

            subject = 'Todo App: Password Reset Requested'
            message = render_to_string(
                'accounts/passwordResetEmailTemplate.html',
                {'password_reset_link': password_reset_link}
            )

            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
                messages.success(request, f'A PASSWORD RESET EMAIL HAS BEEN SENT TO "{user.email}" ')
            except:
                messages.error(request, f'Failed to send Email. Check your Internet Connection')

            return redirect('login')
        else:
            messages.error(request, "ERROR: No user account associated with the provided email.")
    else:
        pass

    context = {'page': page}
    return render(request, 'accounts/passwordResetForm.html', context)


def passwordResetConfirm(request, uid, token):
    page = 'passwordResetConfirm'

    if request.user.is_authenticated:
        return redirect('viewTasks')

    try:
        userProfile = User.objects.get(id=uid)
    except User.DoesNotExist:
        userProfile = None

    if userProfile is not None and default_token_generator.check_token(userProfile, token):
        email_reset_link_success = True

        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 == password2:
                userProfile.set_password(password1)
                userProfile.save()

                messages.success(request, 'Password updated successfully.')

                login(request, userProfile)

                return redirect('viewTasks')
            else:
                messages.error(request, 'ERROR: New passwords do not match.')

    else:
        email_reset_link_success = False
        messages.error(request, "The password reset link is invalid or has expired.")

    context = {'page': page, 'email_reset_link_success': email_reset_link_success}
    return render(request, 'accounts/editUserPassword.html', context)
