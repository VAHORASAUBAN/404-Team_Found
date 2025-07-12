from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_register, name='login'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('browse_questions/', views.browse_questions, name='browse_questions'),
    path('dashboard_home/', views.dashboard_home, name='dashboard_home'),
    path('question_detail/', views.question_detail, name='question_detail'),
    path('user_profile/', views.user_profile, name='user_profile'),
]