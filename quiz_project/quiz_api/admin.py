from django.contrib import admin
from .models import (
    Subject, SchoolClass,
    Quiz, Question,
    Choice, StudentAnswer, 
    StudentAttempt, AttendanceSystem,
    QuizInvitation
)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject']

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['id', 'class_name']

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(StudentAnswer)
admin.site.register(StudentAttempt)
admin.site.register(AttendanceSystem)

@admin.register(QuizInvitation)
class QuizInviteAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'email', 'token', 'is_used']
