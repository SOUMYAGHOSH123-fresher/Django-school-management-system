from django.core.mail import send_mail, get_connection
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import QuizInvitation, StudentAttempt

import threading


def get_token_for_user(user):
    if not user.is_active or not user.is_approved:
        raise AuthenticationFailed("User Account is not active or approved Yet.")
        
    tokens = RefreshToken.for_user(user)
    tokens['role'] = user.role
    tokens['email'] = user.email

    return {
        'refresh': str(tokens),
        'access': str(tokens.access_token)
    }

def send_reset_email(email, url):
    message = f"""
        Click below to reset your password

        <a href="{url}">
            Reset Password
        </a>
    """
    threading.Thread(
        target=send_mail,
        kwargs={
            "subject": "Send the reset Password Link",
            "message": message,
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [email],
            "fail_silently": True,
        }
    ).start()
    return email

def send_quiz_email(quiz, student_emails):
    subject = f"New Quiz: {quiz.title}"

    # 1. Bulk create invitations
    invitations = []
    for email in student_emails:
        if StudentAttempt.objects.filter(
            quiz=quiz,
            student__email=email,
            completed=True).exists():
            continue

        invitations.append(
            QuizInvitation(
                quiz=quiz, 
                email=email
            )
        )
    
    QuizInvitation.objects.bulk_create(invitations, ignore_conflicts=True)

    # 2. Fetch invitations with tokens
    invitations = QuizInvitation.objects.filter(
        quiz=quiz, email__in = student_emails
    )

    # 3. Open ONE email connection
    connection = get_connection()
    connection.open()

    messages = []

    for invitation in invitations:
        target_url =f"http://127.0.0.1:8000/api/quiz/invite/{invitation.token}/"

        # Context data for the template
        context = {
            'quiz_title': quiz.title,
            'subject': quiz.subject.subject,
            'teacher_name': quiz.teacher.get_full_name() or quiz.teacher.email,
            'quiz_type': quiz.get_quiz_type_display(),
            'quiz_id': quiz.id,
            'invite_url': target_url
        }

        # Render HTML and create a plain-text version for backup
        html_content = render_to_string('emails/new_quiz_notification.html', context)
        text_content = strip_tags(html_content) 

        msg = EmailMultiAlternatives(
            subject, 
            text_content, 
            settings.EMAIL_HOST_USER, 
            [invitation.email],
            connection=connection
        )
        msg.attach_alternative(html_content, "text/html")
        messages.append(msg)

    # 4. Send all emails in ONE go
    connection.send_messages(messages)
    connection.close()

    return len(messages)

def send_user_email(email):
    threading.Thread(
        target=send_mail,
        kwargs={
            "subject": "Account Created",
            "message": "Your account has been created and approved",
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [email],
        }
    ).start()

def send_create_user_email(email):
    threading.Thread(
        target=send_mail,
        kwargs={
            "subject": "Account Created",
            "message": "Thank you for registering. Please wait until the account is approve.",
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [email],
            "fail_silently": True,
        }
    ).start()

def send_approve_user_email(email):
    threading.Thread(
        target=send_mail,
        kwargs={
            "subject": "Account Created",
            "message": "Thank you for registering. Your account has been created and approved. You can now login and start using the system.",
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [email],
            "fail_silently": True,
        }
    ).start()

def send_reject_user_email(email):
    threading.Thread(
        target=send_mail,
        kwargs={
            "subject": "Your Account is Rejected.",
            "message": "Thank you for registering. Your account has not been approved. You are not the part of our system.",
            "from_email": settings.EMAIL_HOST_USER,
            "recipient_list": [email],
            "fail_silently": True,
        }
    ).start()


