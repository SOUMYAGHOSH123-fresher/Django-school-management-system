from .models import *
from .serializer import *
from .services import send_quiz_email, send_user_email, send_approve_user_email, send_reject_user_email
from .cuspermit import (
    IsPrincipal, IsTeacher, IsOwnerOrReadOnly, 
    IsStudent, IsTeacherOrStudent, IsPrincipalOrTeacher
    )

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from django.shortcuts import render
from django.utils.timezone import now
from django.core.mail import send_mail
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend

from datetime import timedelta

import threading
import uuid
import logging
logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpRequest:
    return render(request, 'index.html')

def teacher_page(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/teacher_dashboard.html")

def principal_page(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/principal_dashboard.html")

def student_page(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard/student_dashboard.html")

def DashboardView(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")

# =======================  Principel Dashboard  ====================
class PrincipalDashboardAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    login_url = 'auth/login-user/'  
    redirect_field_name = 'next'

    def get(self, request: Request) -> Response:
        teachers = User.objects.filter(role='teacher', is_approved=True)
        students = User.objects.filter(role='student')
        quizzes = Quiz.objects.all()

        active_quizzes = quizzes.filter(is_active=True).count()
        inactive_quizzes = quizzes.filter(is_active=False).count()

        # Students per class
        class_data = (
            students.values('student_class__class_name')
            .annotate(count=Count('id'))
        )

        class_labels = [c['student_class__class_name'] or "Unknown" for c in class_data]
        class_counts = [c['count'] for c in class_data]

        # Attempts (last 7 days)
        last_7_days = now() - timedelta(days=7)

        attempts_data = (
            StudentAttempt.objects
            .filter(attempt_at__gte=last_7_days)
            .annotate(date=TruncDate('attempt_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        attempt_labels = [str(a['date']) for a in attempts_data]
        attempt_counts = [a['count'] for a in attempts_data]

        return Response({
            "teachers": teachers.count(),
            "students": students.count(),
            "quizzes": quizzes.count(),
            "active_quizzes": active_quizzes,
            "inactive_quizzes": inactive_quizzes,
            "class_labels": class_labels,
            "class_counts": class_counts,
            "attempt_labels": attempt_labels,
            "attempt_counts": attempt_counts,
        })


class PrincipalTeacherAPI(APIView):
    permission_classes = [IsPrincipal]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['email']
    search_fields = ['=email', '^role']
    
    def get(self, request: Request) -> Response:
        teachers = User.objects.filter(role='teacher').select_related('subject').order_by('-id')
        subjects = Subject.objects.all()
        serializer = UserSerializer(teachers, many=True)
        sub_ser = SubjectSerializer(subjects, many=True)
        return Response({
            'teachers': serializer.data,
            'subjects': sub_ser.data
        })


class ToogleTeacherAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({
                'error': 'User Not Found'
            })
        
        user.is_approved = not user.is_approved

        if user.is_approved:
            send_approve_user_email(user.email)
        else: 
            send_reject_user_email(user.email)
            
        user.save()
        return Response({"success": True, "message": 'Teacher Status Changed'})


class DeleteTeacherAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({
                'error': 'User Not Found'
            })
        
        user.delete()
        return Response({
            'success': True, 
            'message': 'Teacher deleted'
        }, status=200)


class PrincipalStudentAPI(APIView):
    permission_classes = [IsPrincipal]

    def get(self, request: Request) -> Response:
        students = User.objects.filter(role='student').select_related('student_class').order_by('-id')
        classes = SchoolClass.objects.all()

        stu_serializer = UserSerializer(students, many=True)
        class_serializer = SchoolClassSerializer(classes, many=True)

        return Response({
            'students': stu_serializer.data,
            'classes': class_serializer.data
        })


class ToogleUserAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({
                'error': 'User Not Found'
            })
        
        user.is_approved = not user.is_approved

        if user.is_approved:
            send_approve_user_email(user.email)
        else: 
            send_reject_user_email(user.email)
            
        user.save()
        return Response({"success": True, "message": 'approved'})


class DeleteUserAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({
                'error': 'User Not Found'
            })
        
        user.delete()
        return Response({
            'success': True, 
            'message': 'user deleted'
        }, status=200)


class PrincipalQuizzAPIView(APIView):
    permission_classes = [IsPrincipal]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'quiz_type']


    def get(self, request: Request) -> Response:
        quizzes = Quiz.objects.select_related(
            'subject', 'student_class', 'teacher'
        ).annotate(
            total_students = Count('quizinvitation'),
            total_attempts = Count('studentattempt')
        ).order_by('-created_at')

        serializer  = QuizSerializer(quizzes, many=True)
        return Response({
            'quizzes': serializer.data
        })


class ToogleQuizAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            logger.warning('quiz not found')
            return Response({
                'error': 'Quiz Not FOund'
            }, status=404)
        
        quiz.is_active = not quiz.is_active
        quiz.save()
        return Response({
            'message': 'Quiz Update',
            "success": True
        })


class DeleteQuizApi(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request, id: int) -> Response:
        try:
            quiz = Quiz.objects.get(id=id)
        except Quiz.DoesNotExist:
            logger.warning('quiz not found')
            return Response({
                'error': 'Quiz Not FOund'
            }, status=404)
        
        quiz.delete()
        return Response({
            'message': 'Delete Quiz',
            "success": True
        })

# =================  Teacher  ============================
class GetClassAPI(ListAPIView):
    queryset = SchoolClass.objects.all().order_by('class_name')
    serializer_class = SchoolClassSerializer


class GetSubjectAPI(ListAPIView):
    queryset = Subject.objects.all().order_by('subject')
    serializer_class = SubjectSerializer
    

class TeacherDashboardAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request: Request) -> Response:
        quizzes = Quiz.objects.filter(
            teacher=request.user,
            is_active = True
        ).annotate(
            total_students = Count('studentattempt')
        ).order_by('-created_at')

        total_attempts = StudentAttempt.objects.filter(
                quiz__teacher=request.user
            ).count()

        serializer = QuizSerializer(quizzes, many=True)

        return Response({
            'quizzes': serializer.data,
            'total_attempts': total_attempts
        })


class CreateQuizAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request: Request) -> Response:
        quizzes = Quiz.objects.select_related('teacher', 'subject')
        serializer = QuizSerializer(quizzes, many=True)
        return Response({
            'count': quizzes.count(),
            'data': serializer.data
        })

    def post(self, request: Request) -> Response: 
        serializer = QuizSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.error(f'Error: {serializer.errors}') 
            return Response({
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(
            teacher = request.user,
            subject = request.user.subject
        )

        logger.info(f'Quiz created successfully by {request.user}') 
        return Response({
            'success': True,
            'message': 'Quiz created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class QuizRetrieveUpdateDeleteAPI(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request: Request, id: int) -> Response:
        try:
            quiz = Quiz.objects.prefetch_related(
                'questions__choices'
            ).get(id=id, teacher=request.user)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)

        serializer = QuizSerializer(quiz)
        return Response(serializer.data)
    
    def put(self, request: Request, id: int) -> Response:
        try:
            quiz = Quiz.objects.prefetch_related(
                'questions__choices'
            ).get(id=id, teacher=request.user)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)
        
        serializer = QuizSerializer(quiz, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(
            teacher = request.user,
            subject = request.user.subject
        )

        logger.info(f"Quiz Updated Successfully by {request.user}")
        return Response({
            'message': 'Quiz Updated Successsfully',
            'data': serializer.data
        })
    
    def delete(self, request: Request, id: int):
        try:
            quiz = Quiz.objects.prefetch_related(
                'questions__choices'
            ).get(id=id, teacher=request.user)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)
        
        quiz.delete()

        logger.info(f"Quiz Deleted Successfully by {request.user}")
        return Response({
            'message': 'Quiz Deleted Successsfully'
        })


class SendQuizLinkToStudentAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request: Request) -> Response:
        quizzes = QuizSerializer(
            Quiz.objects.filter(    
                teacher=request.user, is_active=True
            ).select_related(
                'student_class'
            ).prefetch_related('questions__choices'), 
            many=True)
        
        students = UserSerializer(
            User.objects.filter(role='student', is_approved=True).select_related('student_class'),
            many=True
        )

        return Response({
            'quizzes': quizzes.data,
            'students': students.data
        })
    
    def post(self, request: Request) -> Response:
        quiz_id = request.data.get('quiz_id')
        emails = request.data.get('emails')

        if not isinstance(emails, list):
            return Response({'error': 'Emails must be a list'}, status=400)

        if not quiz_id or not emails:
            logger.warning("quiz id and email are required.")
            return Response({
                'error': 'quiz id and email are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quiz = Quiz.objects.get(id=quiz_id, teacher=request.user)
        except Quiz.DoesNotExist:
            logger.error("Quiz is Not Found.")
            return Response({  
                'error': 'Quiz is Not Found'
            })

        threading.Thread(
            target=send_quiz_email,
            args=(quiz, emails)
        ).start()

        logger.info("Email are being Send to all students.")
        return Response({
            'message': 'Email are being Send to all students'
        })


class BulkStudentUploaAPI(APIView):
    permission_classes = [IsPrincipalOrTeacher]

    def post(self, request) -> Response:
        data = request.data

        # check data in list format or not
        if not isinstance(data, list):
            logger.warning("Expected a List of Students")
            return Response({
                'error': 'Expected a List of Students'
            }, status=400)
        
        class_map = {
            s.class_name.lower(): s
            for s in SchoolClass.objects.all()
        }

        emails = [s['email'] for s in data]
        existing_emails = set(
            User.objects.filter(email__in=emails)
            .values_list('email', flat=True)
        )
        
        users = []
        success = []
        errors = []

        for s in data:
            email = s.get('email')
            password = s.get('password')
            class_name = s.get('class_name', '').lower()
            role = s.get('role')

            if email in existing_emails:
                errors.append({'email': 'Email aready exists.'})
                continue

            if len(password) < 5:
                errors.append({email: "Weak password"})
                continue

            if role != 'student':
                errors.append({email: 'Role must be Student'})
                continue

            school_class = class_map.get(class_name)
            if not school_class:
                errors.append({email: "Invalid class name"})
                continue
            else:
                school_class = SchoolClass.objects.get(class_name__icontains=class_name)

            user = User(
                email=email,
                first_name=s.get('first_name'),
                last_name=s.get('last_name'),
                role= role,
                is_approved=True,
                student_class=school_class
            )
            user.set_password(password)
            users.append(user)
            success.append(email)

        # bulk insert (FAST)
        created_users = User.objects.bulk_create(users)

        # bulk create profiles
        profiles = [
            Profile(
                user=user
            )
            for user in created_users
        ]

        Profile.objects.bulk_create(profiles)

        # async emails (NON-BLOCKING)
        for email in success:
            send_user_email(email)

        logger.info("successfully uploaded.")
        return Response({
            "created": success,
            "failed": errors,
            "message": f"{len(success)} students uploaded successfully"
        }, status=200)


class BulkTeacherUploaAPI(APIView):
    permission_classes = [IsPrincipal]

    def post(self, request: Request) -> Response:
        data = request.data

        # check data in list format or not
        if not isinstance(data, list):
            logger.warning("Expected a List of Teachers")
            return Response({
                'error': 'Expected a List of Teachers'
            }, status=400)
        
        subjects_map = {
            s.subject.lower(): s
            for s in Subject.objects.all()
        }

        emails = [t['email'] for t in data]
        existing_emails = set(
            User.objects.filter(email__in=emails)
            .values_list('email', flat=True)
        )
        
        users = []
        success = []
        errors = []

        for t in data:
            email = t.get('email')
            password = t.get('password')
            subject_name = t.get('subject', '').lower()
            role = t.get('role')

            if email in existing_emails:
                errors.append({email: 'Email aready exists.'})
                continue

            if len(password) < 5:
                errors.append({email: "Weak password"})
                continue

            if role != 'teacher':
                errors.append({email: 'Role must be Teacher'})
                continue

            subject = subjects_map.get(subject_name)
            if not subject:
                errors.append({email: "Invalid subject"})
                continue
            else:
                subject = Subject.objects.get(subject__icontains=subject)

            user = User(
                email=email,
                first_name=t.get('first_name'),
                last_name=t.get('last_name'),
                role='teacher',
                is_approved=True,
                subject=subject
            )
            user.set_password(password)
            users.append(user)
            success.append(email)

        # bulk insert (FAST)
        created_users = User.objects.bulk_create(users)

        # bulk create profiles
        profiles = [
            Profile(
                user=user
            )
            for user in created_users
        ]

        Profile.objects.bulk_create(profiles)
        
        # async emails
        for email in success:
            send_user_email(email)

        logger.info("teacher added successfully")
        return Response({
            "created": success,
            "failed": errors,
            "message": 'Student uploaded Successfully.'
        }, status=200)


# ==============================  STudent  ================================
class StudentDashboardAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request: Request) -> Response: 
        quizzes = Quiz.objects.filter(
            student_class=request.user.student_class, 
            is_active=True
        )
        
        attempts = StudentAttempt.objects.filter(
                student=request.user, completed=True
            ).select_related('quiz')
        
        stats = attempts.aggregate(
            total_attempts=Count('id'),
            avg_score=Avg('score')
        )

        invites = QuizInvitation.objects.filter(
                email = request.user.email,
                is_used = False
            ).select_related('quiz')

        logger.info(f"invitations data {invites.count()}")
        invitations = QuizInvitationSerializer(invites, many=True)

        serializer = StudentAttemptSerializer(attempts, many=True)
        return Response({
            'total_quizzes': quizzes.count(),
            'attempts': serializer.data,
            'stats': {
                'total_attempts': stats['total_attempts'],
                'avg_score': stats['avg_score']
            },
            'invitations': invitations.data
        })


class ValidateQuizTokenAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request: Request, token: uuid.UUID) -> Response:
        try:
            invite = QuizInvitation.objects.get(token=token, is_used=False)

        except QuizInvitation.DoesNotExist:
            logger.warning(f"Invalid or expired token {token}")
            return Response({
                'error': 'Invalid or Expired Token'
            })
        
        if invite.email.lower() != request.user.email.lower():
            logger.warning(f"You are not eligible to attempt the Test")
            return Response({
                'message': 'You are not eligible to attempt the Test.'
            })
        
        logger.info(f"{invite.started_At}")
        if not invite.started_At:
            invite.started_At = now()
            invite.save()

        serializer = QuizSerializer(invite.quiz)
        return Response({
            'quiz': serializer.data,
            'email': invite.email,
            "duration": invite.quiz.duration,
            'started_at': invite.started_At
        })


class SubmitQuizAPI(APIView):
    permission_classes = [IsStudent]

    def post(self, request: Request, token: str) -> Response:
        try:
            invite = QuizInvitation.objects.select_related('quiz').get(token=token, is_used=False)

        except QuizInvitation.DoesNotExist:
            logger.warning(f"Invalid token or Expired token {token}")
            return Response({
                'error': 'Invalid token or Expired token'
            }, status=400)
        
        quiz = invite.quiz

        if not invite.started_At:
            logger.warning("Quiz not started properly.")
            return Response({
                'error': 'Quiz not started properly'
            }, status=400)
                
        answers = request.data.get('answers', [])

        if not answers:
            logger.warning("Answer are Required.")
            return Response({'error': 'Answer are Required'})

        try:
            user = User.objects.get(email=invite.email)
        except User.DoesNotExist:
            logger.warning(F"Invalid User {invite.email}")
            return Response({'error': 'Invalid user'}, status=status.HTTP_404_NOT_FOUND)
        
        attempt, created = StudentAttempt.objects.get_or_create(
            quiz = quiz, 
            student=user,
            defaults={
                'score': 0,
                'completed': False
            })
        
        if not created:
            logger.warning(f"Quiz Attempt already by {invite.email}")
            return Response({'error': 'Attempt already'})
        
        if attempt.completed:
            return Response({'error': 'Already submitted'})

        end_time = invite.started_At + timedelta(minutes=quiz.duration)

        if now() > end_time:
            attempt.completed = True
            attempt.save()
            
            invite.is_used =True
            invite.save()

            logger.info("Time is Over, Quiz is auto submitted.")
            return Response({
                'message': 'Time is Over',
                'score': attempt.score,
                "attempt_id": attempt.id
            })
        
        questions_list = list(quiz.questions.all())

        if len(answers) < len(questions_list):
            return Response({'error': "Partial attempt not accepted"})

        questions = {
            q.id: q for q in questions_list
        }

        choices = {
            c.id: c for c in Choice.objects.filter(question__quiz=quiz)
        }

        total_score = 0
        percentage = 0
        answers_to_create = []

        try:
            with transaction.atomic():
                for answer in answers:
                    question = questions.get(int(answer['ques_id']))
                    choice = choices.get(int(answer['option_id']))

                    if not question or not choice:
                        logger.warning("Invalid question or choice")
                        return Response({'error': 'Invalid question/choice'}, status=400)

                    if choice.question_id != question.id:
                        logger.warning("Invalid mapping")
                        return Response({'error': 'Invalid mapping'}, status=400)

                    answers_to_create.append(
                        StudentAnswer(
                            attempt=attempt,
                            question=question,
                            select_answer=choice
                        )
                    )
                    
                    if choice.is_true:
                        total_score += question.mark

                StudentAnswer.objects.bulk_create(answers_to_create)

                total_marks = sum(q.mark for q in questions_list)
                attempt.total_marks = total_marks
                attempt.score = total_score
                attempt.completed = True
                attempt.save()

                percentage = (total_score / total_marks) * 100 if total_marks else 0

                invite.is_used = True
                invite.save()
                
            
        except Exception as e:
            logger.error(f"Something went wrong {str(e)}")
            return Response({
                'error': str(e)
            }, status=400)
        
        logger.info(f"Quiz submitted successfull by {invite.email}")
        return Response({
            "message": "Quiz submitted successfully, wait for result",
            "score": total_score,
            "total_questions": quiz.questions.count(),
            "percentage": percentage,
            'attempt_id': attempt.id
        })


class ShowTestResultAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request: Request, id: int) -> Response:
        attempt = StudentAttempt.objects.select_related('quiz').get(id=id, student=request.user)
        
        results = StudentAnswer.objects.filter(attempt=attempt).select_related(
            'question', 'select_answer'
        ).prefetch_related('question__choices')
        print('results', results)

        serializer = ResultSerializer(results, many=True)
        return Response({
            'quiz': attempt.quiz.title,
            "quiz_id": attempt.quiz.id,
            'score': attempt.score,
            'results': serializer.data
        })


class ShowAttemptHistoryAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request: Request) -> Response:
        attempt_histories = StudentAttempt.objects.filter(
            student=request.user,
            completed=True
        )
        serializer = StudentAttemptSerializer(attempt_histories, many=True)
        return Response({
            'histories': serializer.data
        })

# =====================  For All Authenticated User   =======================
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Cast

class LeaderboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, id: int) -> Response:
        attempts = list(
            StudentAttempt.objects.filter(
                quiz=id,
                completed=True
            ).select_related(
                'student'
            ).annotate(
                percentage=ExpressionWrapper(
                    (F('score') * 100.0) / F('total_marks'),
                    output_field=FloatField()
                )
            ).order_by('-score', 'attempt_at')
        )[:20]

        leaderboard = []
        prev_score = None
        rank = 0

        for index, attempt in enumerate(attempts):
            if attempt.score != prev_score:
                rank = index + 1
                prev_score = attempt.score

            leaderboard.append({
                "rank": rank,
                "student": attempt.student.email,
                "score": attempt.score,
                "percentage": round(attempt.percentage, 2),
                "submitted_at": attempt.attempt_at
            })

        return Response({
            "id": id,
            "leaderboard": leaderboard
        })


class PuchInAttendenceAPI(APIView):
    permission_classes = [IsTeacherOrStudent]

    def post(self, request: Request) -> Response:
        date = now().date()
        attendance, _ = AttendanceSystem.objects.get_or_create(
            user=request.user,
            date = date
        )

        if attendance.punch_in:
            logger.warning("You are alredy punch in ")
            return Response({
                'error': 'You are alredy punch in'
            }, status=400)

        attendance.punch_in = now()
        if attendance.punch_in.hour > 9:
            attendance.status = 'late'

        attendance.save()
        logger.info(f"Punch-in successfully by {request.user.email}")
        return Response({
            "message": "Punch-in successful",
            "Punch_in": attendance.punch_in
        })
    

class PunchOutAttendanceAPI(APIView):
    permission_classes = [IsTeacherOrStudent]

    def post(self, request: Request) -> Response:
        date = now().date()
        attendance, _ = AttendanceSystem.objects.get_or_create(
            user=request.user,
            date = date
        )

        if not attendance.status:
            logger.error("You are not Punched In")
            return Response({
                'error': 'You are not Punched in.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance.punch_out:
            logger.warning("You are already Punched out")
            return Response({
                'error': 'You are already Punched out.'
            }, status=status.HTTP_400_BAD_REQUEST)

        attendance.punch_out = now()
        duration = attendance.punch_out - attendance.punch_in
        attendance.total_hour = duration.total_seconds() / 3600

        attendance.save()
        logger.info("You are successfully Punched out")
        return Response({
            'message': 'You are successfully Punched out',
            'total_hour': round(attendance.total_hour, 2)
        })


class DailyAttendanceViewAPI(APIView):
    def get(self, request: Request) -> Response:
        user = request.user
        today = now().date()

        try:
            attendance = AttendanceSystem.objects.get(
                user = user,
                date =today
            )
        except AttendanceSystem.DoesNotExist:
            return Response({
                'punch_in': None,
                'punch_out': None,
                'status': None,
                'total_hour': None
            }, status=200)
        
        return Response({
            'punch_in': attendance.punch_in,
            'punch_out': attendance.punch_out,
            'status': attendance.status,
            'total_hour': attendance.total_hour
        })

# ==============  IN MISMATCH URL  ==================
def custom_404(request: HttpRequest, exception) -> HttpResponse:
    ignore_paths = ['/favicon.ico', '/robots.txt']

    if request.path in ignore_paths:
        return JsonResponse({'error': 'Not found'}, status=404)

    logger.warning(f"404 Not Found: {request.path}")
    return render(request, "404.html", status=404)

def custom_500(request: HttpRequest) -> HttpResponse:
    logger.error(f"Server error occurred: {request.path}")
    return render(request, "500.html", status=500)

