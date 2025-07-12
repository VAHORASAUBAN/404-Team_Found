from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_register, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('browse_questions/', views.browse_questions, name='browse_questions'),
    path('dashboard_home/', views.dashboard_home, name='dashboard_home'),
    path('question_detail/', views.question_detail, name='question_detail'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('questions/filter/', views.questions_filter, name='questions_filter'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
