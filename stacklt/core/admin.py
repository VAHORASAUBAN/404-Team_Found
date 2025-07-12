from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    User, OTP, Tag, Question, Answer, Comment,
    Vote, Notification, ActivityLog, Feedback,
    Report, UserBadge
)

# -----------------------------
# Custom User Admin
# -----------------------------


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("username", "email", "role",
                    "is_email_confirmed", "is_staff")
    list_filter = ("role", "is_email_confirmed", "is_staff")
    search_fields = ("username", "email", "full_name")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile Info", {
            "fields": ("full_name", "bio", "profession", "website", "github", "linkedin", "twitter", "profile_image")
        }),
        ("Custom Flags", {"fields": ("role", "is_email_confirmed")}),
    )


# -----------------------------
# Generic Inline for Votes
# -----------------------------

class VoteInline(GenericTabularInline):
    model = Vote
    extra = 0


# -----------------------------
# Question Admin
# -----------------------------

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)
    inlines = [VoteInline]


# -----------------------------
# Answer Admin
# -----------------------------

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "user", "is_accepted", "created_at")
    list_filter = ("is_accepted", "created_at")
    search_fields = ("text",)
    inlines = [VoteInline]


# -----------------------------
# Comment Admin
# -----------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("answer", "user", "created_at")
    search_fields = ("content",)
    inlines = [VoteInline]


# -----------------------------
# Tag Admin
# -----------------------------

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# -----------------------------
# OTP Admin
# -----------------------------

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at")
    search_fields = ("user__username", "code")


# -----------------------------
# Notification Admin
# -----------------------------

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read",)


# -----------------------------
# Activity Log Admin
# -----------------------------

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "target", "created_at")
    search_fields = ("action", "target")


# -----------------------------
# Feedback Admin
# -----------------------------

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "created_at")
    search_fields = ("message",)


# -----------------------------
# Report Admin
# -----------------------------

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "reason", "created_at")
    search_fields = ("reason",)


# -----------------------------
# UserBadge Admin
# -----------------------------

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge_name", "awarded_at")
    search_fields = ("badge_name",)
