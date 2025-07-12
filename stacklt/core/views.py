from django.shortcuts import render

# Create your views here.
def login_register(request):
    return render(request, 'login_register.html')

def ask_question(request):
    return render(request, 'ask_question.html')

def question_detail(request):
    return render(request, 'question_detail.html')

def user_profile(request):
    return render(request, 'user_profile.html')

def browse_questions(request):
    return render(request, 'browse_questions.html')

def dashboard_home(request):
    return render(request, 'dashboard_home.html')