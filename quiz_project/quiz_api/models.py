from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
import uuid
from django.utils.timezone import now
from datetime import timezone
import random


class Subject(models.Model):
    subject = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject


class SchoolClass(models.Model):
    class_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.class_name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('email must be defined')
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'principal') 

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Staff must be True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser muust be true')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='email address')
    ROLE_CHOICES = (
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(choices=ROLE_CHOICES, default='student', null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, help_text='only for the teacher')
    student_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, blank=True, help_text='only for the student')
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    objects = CustomUserManager()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'principal'
            self.is_approved = True

        return super().save(*args, **kwargs) 
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, null=True, blank=True, default='xxxxxxxxxx')
    bio = models.TextField(null=True, blank=True, default='User Profile')
    address = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} profile'


class Quiz(models.Model):
    QUIZ_CHOICES = (
        ('mid', 'Mid Term Test'), 
        ('quarter', 'Quarterly Test'),
        ('practice', 'Practice Test'),
        ('final', 'Final Test')
    )
    title = models.CharField(max_length=255, verbose_name='Test name')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'}, related_name='quizs')
    quiz_type = models.CharField(max_length=20, choices=QUIZ_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    duration = models.IntegerField(default=10, help_text='Duration in Minutes')

    def __str__(self):
        return F'{self.title} - {self.quiz_type} - {self.teacher}'


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()  
    mark = models.IntegerField(default=1) 

    def __str__(self):
        return self.question


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    option = models.TextField()
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.option[:20]} - {self.is_true}'


class QuizInvitation(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    created_At = models.DateTimeField(auto_now_add=True)

    started_At = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email


class StudentAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='studentattempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    attempt_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quiz', 'student')
        indexes = [
            models.Index(fields=['quiz', 'completed']),
            models.Index(fields=['quiz', 'student']),
        ]

    def __str__(self):
        return f'{self.student.email} - {self.quiz.title} - {self.completed}'
    

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    select_answer = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.attempt.student} - {self.question}'


class AttendanceSystem(models.Model):
    SELECT_CHOICE = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    punch_in = models.DateTimeField(null=True, blank=True)
    punch_out = models.DateTimeField(null=True, blank=True)
    total_hour = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=10, choices=SELECT_CHOICE, default='present')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.email} - {self.status}"

