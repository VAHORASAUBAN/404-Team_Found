from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

# Create your views here.


def login_register(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            # Handle login
            username_or_email = request.POST.get('email')
            password = request.POST.get('password')

            # Try to authenticate with username first, then email
            user = authenticate(
                request, username=username_or_email, password=password)
            if not user:
                # Try to find user by email and authenticate
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(
                        request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('dashboard_home')
            else:
                messages.error(request, 'Invalid username/email or password.')

        elif action == 'register':
            # Handle registration
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirmPassword')

            # Validation
            errors = []

            if password != confirm_password:
                errors.append('Passwords do not match.')

            if User.objects.filter(username=username).exists():
                errors.append('Username already exists.')

            if User.objects.filter(email=email).exists():
                errors.append('Email already exists.')

            if len(password) < 8:
                errors.append('Password must be at least 8 characters long.')

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(
                    request, 'Account created successfully! Please log in.')
                return redirect('login')

    return render(request, 'login_register.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def ask_question(request):
    return render(request, 'ask_question.html')


@login_required
def question_detail(request):
    return render(request, 'question_detail.html')


@login_required
def user_profile(request):
    return render(request, 'user_profile.html')


@login_required
def browse_questions(request):
    return render(request, 'browse_questions.html')


@login_required
def dashboard_home(request):
    return render(request, 'dashboard_home.html')
