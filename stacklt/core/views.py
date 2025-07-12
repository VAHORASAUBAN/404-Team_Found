
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.db import models
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
import json
import time
from .models import User, Question, Tag, Answer, Vote

# AJAX endpoint for filtering questions


@login_required
@require_GET
def questions_filter(request):
    tab = request.GET.get('tab', 'trending')
    if tab == 'newest':
        questions = Question.objects.select_related(
            'user').prefetch_related('tags').order_by('-created_at')
    elif tab == 'unanswered':
        questions = Question.objects.select_related('user').prefetch_related('tags').annotate(
            num_answers=models.Count('answers')).filter(num_answers=0).order_by('-created_at')
    else:  # trending (for demo, just order by most answers)
        questions = Question.objects.select_related('user').prefetch_related('tags').annotate(
            num_answers=models.Count('answers')).order_by('-num_answers', '-created_at')
    html = render_to_string('partials/questions_grid.html',
                            {'questions': questions}, request=request)
    return JsonResponse({'html': html})


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
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        tags = request.POST.get('tags', '')
        tone = request.POST.get('tone', 'beginner')

        # Validation
        errors = []
        if not title or len(title.strip()) < 10:
            errors.append(
                'Question title must be at least 10 characters long.')

        if not description or len(description.strip()) < 30:
            errors.append(
                'Question description must be at least 30 characters long.')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create the question
            question = Question.objects.create(
                title=title.strip(),
                description=description.strip(),
                user=request.user
            )

            # Handle tags
            if tags:
                tag_list = [tag.strip().lower()
                            for tag in tags.split(',') if tag.strip()]
                for tag_name in tag_list[:5]:  # Limit to 5 tags
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    question.tags.add(tag)

            messages.success(request, 'Question posted successfully!')
            return redirect('question_detail', pk=question.pk)

    # Get popular tags for suggestions
    popular_tags = Tag.objects.all()[:20]
    import json
    popular_tags_json = json.dumps([tag.name for tag in popular_tags])

    context = {
        'popular_tags': popular_tags,
        'popular_tags_json': popular_tags_json,
        'user': request.user
    }
    return render(request, 'ask_question.html', context)


@login_required
def question_detail(request, pk=None):
    if pk:
        try:
            question = Question.objects.get(pk=pk)
            context = {
                'question': question,
                'user': request.user
            }
            return render(request, 'question_detail.html', context)
        except Question.DoesNotExist:
            messages.error(request, 'Question not found.')
            return redirect('browse_questions')
    return render(request, 'question_detail.html')


@login_required
def user_profile(request):
    # Handle profile update
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            user = request.user

            # Update basic profile info
            full_name = request.POST.get('full_name', '').strip()
            bio = request.POST.get('bio', '').strip()
            profession = request.POST.get('profession', '').strip()
            website = request.POST.get('website', '').strip()
            github = request.POST.get('github', '').strip()
            linkedin = request.POST.get('linkedin', '').strip()
            twitter = request.POST.get('twitter', '').strip()

            # Update user fields
            user.full_name = full_name
            user.bio = bio
            user.profession = profession
            user.website = website
            user.github = github
            user.linkedin = linkedin
            user.twitter = twitter

            # Handle profile image upload with better error handling
            if 'profile_image' in request.FILES:
                profile_image = request.FILES['profile_image']
                if profile_image and profile_image.size > 0:
                    # Remove old profile image if exists
                    if user.profile_image:
                        try:
                            user.profile_image.delete(save=False)
                        except:
                            pass  # Ignore if old file doesn't exist

                    user.profile_image = profile_image
                    messages.success(
                        request, f'Profile picture updated successfully!')
                else:
                    messages.warning(
                        request, 'No valid image file was uploaded.')

            try:
                user.save()
                messages.success(request, 'Profile updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')

            return redirect('user_profile')

    # Get user's questions and answers count
    from .models import Question, Answer, Vote
    from django.db.models import Count

    user = request.user
    questions_count = Question.objects.filter(user=user).count()
    answers_count = Answer.objects.filter(user=user).count()

    # Calculate helpful votes (upvotes on user's questions and answers)
    helpful_votes = 0
    user_questions = Question.objects.filter(user=user)
    user_answers = Answer.objects.filter(user=user)

    # Count upvotes on questions and answers
    from django.contrib.contenttypes.models import ContentType
    question_ct = ContentType.objects.get_for_model(Question)
    answer_ct = ContentType.objects.get_for_model(Answer)

    for question in user_questions:
        helpful_votes += Vote.objects.filter(
            content_type=question_ct,
            object_id=question.id,
            vote_type='up'
        ).count()

    for answer in user_answers:
        helpful_votes += Vote.objects.filter(
            content_type=answer_ct,
            object_id=answer.id,
            vote_type='up'
        ).count()

    # Get recent questions and answers
    recent_questions = Question.objects.filter(
        user=user).order_by('-created_at')[:5]
    recent_answers = Answer.objects.filter(
        user=user).order_by('-created_at')[:5]

    # Get all questions and answers for tabs
    all_questions = Question.objects.filter(user=user).order_by('-created_at')
    all_answers = Answer.objects.filter(user=user).order_by('-created_at')

    # Calculate reputation (simplified: 10 points per upvote, 5 per accepted answer)
    reputation = helpful_votes * 10
    accepted_answers = Answer.objects.filter(
        user=user, is_accepted=True).count()
    reputation += accepted_answers * 15

    # Calculate AI tools usage (based on questions and answers count)
    ai_tools_used = questions_count + answers_count + (helpful_votes // 5)

    # Get user badges (if any)
    badges = []
    if questions_count >= 10:
        badges.append({'name': 'Top Contributor', 'color': 'warning'})
    if helpful_votes >= 50:
        badges.append({'name': 'AI Power User', 'color': 'primary'})
    if answers_count >= 20:
        badges.append({'name': 'Helper', 'color': 'success'})
    if accepted_answers >= 5:
        badges.append({'name': 'Expert', 'color': 'secondary'})

    # Get recent activity (questions and answers combined)
    from django.db.models import Q
    from datetime import datetime

    # Create activity list with questions and answers
    activities = []

    # Add recent questions to activity
    for question in recent_questions:
        activities.append({
            'type': 'question',
            'action': 'Asked a question',
            'title': question.title,
            'url': 'question_detail',  # You can add proper URL later
            'time': question.created_at,
            'answers_count': question.answers.count(),
            'tags': [tag.name for tag in question.tags.all()[:3]]
        })

    # Add recent answers to activity
    for answer in recent_answers:
        activities.append({
            'type': 'answer',
            'action': 'Answered a question',
            'title': answer.question.title,
            'url': 'question_detail',  # You can add proper URL later
            'time': answer.created_at,
            'is_accepted': answer.is_accepted,
            'upvotes': Vote.objects.filter(
                content_type=answer_ct,
                object_id=answer.id,
                vote_type='up'
            ).count()
        })

    # Sort activities by time
    activities.sort(key=lambda x: x['time'], reverse=True)
    activities = activities[:10]  # Get latest 10 activities

    # Calculate user level based on reputation
    user_level = min(10, max(1, reputation // 100 + 1))
    next_level_threshold = user_level * 100
    points_to_next = next_level_threshold - reputation

    # Calculate leaderboard position (simplified)
    users_with_higher_rep = User.objects.annotate(
        user_reputation=Count('question') * 10 + Count('answer') * 15
    ).filter(user_reputation__gt=reputation).count()
    leaderboard_position = users_with_higher_rep + 1

    context = {
        'user': user,
        'questions_count': questions_count,
        'answers_count': answers_count,
        'helpful_votes': helpful_votes,
        'reputation': reputation,
        'recent_questions': recent_questions,
        'recent_answers': recent_answers,
        'all_questions': all_questions,
        'all_answers': all_answers,
        'badges': badges,
        'accepted_answers': accepted_answers,
        'ai_tools_used': ai_tools_used,
        'activities': activities,
        'user_level': user_level,
        'points_to_next': points_to_next,
        'leaderboard_position': leaderboard_position,
        'cache_buster': int(time.time()),  # Add timestamp for cache busting
    }

    return render(request, 'user_profile.html', context)


@login_required
@login_required
def browse_questions(request):
    questions = Question.objects.all().order_by('-created_at')
    context = {
        'questions': questions,
        'user': request.user
    }
    return render(request, 'browse_questions.html', context)


@login_required
def dashboard_home(request):
    from django.db.models import Count

    # Get recent questions with optimized queries
    questions = Question.objects.select_related('user').prefetch_related('tags').annotate(
        answers_count=Count('answers')
    ).order_by('-created_at')[:10]  # Get latest 10 questions

    user = request.user

    # Get user statistics
    questions_asked = Question.objects.filter(user=user).count()
    answers_given = Answer.objects.filter(user=user).count()

    # Calculate reputation based on votes
    user_questions = Question.objects.filter(user=user)
    user_answers = Answer.objects.filter(user=user)

    reputation = 0
    from django.contrib.contenttypes.models import ContentType
    question_ct = ContentType.objects.get_for_model(Question)
    answer_ct = ContentType.objects.get_for_model(Answer)

    # Count upvotes on user's questions and answers
    for question in user_questions:
        reputation += Vote.objects.filter(
            content_type=question_ct,
            object_id=question.id,
            vote_type='up'
        ).count() * 5  # 5 points per upvote on question

    for answer in user_answers:
        upvotes = Vote.objects.filter(
            content_type=answer_ct,
            object_id=answer.id,
            vote_type='up'
        ).count()
        reputation += upvotes * 10  # 10 points per upvote on answer
        if answer.is_accepted:
            reputation += 15  # 15 points for accepted answer

    # Calculate AI assists (questions with AI-enhanced content)
    ai_assists = questions_asked + answers_given  # Simplified calculation

    # Get trending tags
    trending_tags = Tag.objects.annotate(
        question_count=Count('question')
    ).order_by('-question_count')[:10]

    stats = {
        'questions_asked': questions_asked,
        'answers_given': answers_given,
        'reputation': reputation,
        'ai_assists': ai_assists,
    }

    context = {
        'questions': questions,
        'stats': stats,
        'trending_tags': trending_tags,
        'user': user,
    }

    return render(request, 'dashboard_home.html', context)
