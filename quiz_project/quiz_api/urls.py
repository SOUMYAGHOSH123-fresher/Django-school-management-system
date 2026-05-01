from django.urls import path
from quiz_api import views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # ==================  principal   =========================
    path('dashboard/principal/', views.PrincipalDashboardAPI.as_view(), name='principal_dashboard'),
    path('dashboard/principal/teachers/', views.PrincipalTeacherAPI.as_view(), name='principal_teacher'),
    path('dashboard/principal/teachers/toggle-teacher/<int:id>/', views.ToogleTeacherAPI.as_view(), name='toogle_teacher'),
    path('dashboard/principal/teachers/delete-teacher/<int:id>/', views.DeleteTeacherAPI.as_view(), name='delete_teacher'),
    path('dashboard/principal/students/', views.PrincipalStudentAPI.as_view(), name='principal_student'),
    path('dashboard/principal/quizzes/', views.PrincipalQuizzAPIView.as_view(), name='principal_quizzes'),
    path('dashboard/principal/students/toggle-student/<int:id>/', views.ToogleUserAPI.as_view(), name='toogle_student'),
    path('dashboard/principal/students/delete-student/<int:id>/', views.DeleteUserAPI.as_view(), name='delete_student'),
    path('dashboard/principal/toggle-quiz/<int:id>/', views.ToogleQuizAPI.as_view(), name='toogle_quiz'),
    path('dashboard/principal/delete-quiz/<int:id>/', views.DeleteQuizApi.as_view(), name='delete_quiz'),
    path('dashboard/principal/bulk-teachers/', views.BulkTeacherUploaAPI.as_view(), name='bulk_teachers'),
    path('dashboard/principal/bulk-students/', views.BulkStudentUploaAPI.as_view(), name='bulk_students'),

    # ===================  teacher  =============================
    path('dashboard/teacher/', views.TeacherDashboardAPI.as_view(), name='teacher_dashboard'),
    path('dashboard/teacher/bulk-students/', views.BulkStudentUploaAPI.as_view(), name='teacher_bulk_students'),
    path('dashboard/teacher/create-quiz/', views.CreateQuizAPI.as_view(), name='create_quiz'),
    path('dashboard/teacher/quiz/<int:id>/', views.QuizRetrieveUpdateDeleteAPI.as_view(), name='retrive_update_quiz'),
    path('dashboard/teacher/send-quiz/', views.SendQuizLinkToStudentAPI.as_view(), name='send_quiz_link'),
    path('classes/', views.GetClassAPI.as_view(), name='get_classes'),
    path('subjects/', views.GetSubjectAPI.as_view(), name='get_subject'),

    # ======================== student ==============================
    path('dashboard/student/', views.StudentDashboardAPI.as_view(), name='student_dashboard'),
    path('dashboard/quiz/results/<int:id>/', views.ShowTestResultAPI.as_view(), name='show_result'),
    path("dashboard/student/history/", views.ShowAttemptHistoryAPI.as_view(), name='student_history'),
    path('dashboard/quiz/leaderboard/<int:id>/', views.LeaderboardAPIView.as_view(), name='leaderboard'),
    path('quiz/invite/<uuid:token>/', views.ValidateQuizTokenAPI.as_view(), name='attempt_test'),
    path('quiz/submit/<uuid:token>/', views.SubmitQuizAPI.as_view(), name='submit_test'),

    # ============================  for teacher and student  ===========================
    path('dashboard/attendance/punch-in/', views.PuchInAttendenceAPI.as_view(), name='punch_in'),
    path('dashboard/attendance/punch-out/', views.PunchOutAttendanceAPI.as_view(), name='punch_in'),
    path('dashboard/attendance/checkout/', views.DailyAttendanceViewAPI.as_view(), name='punch_in'),
]