from django.contrib import admin
from django.urls import path, include
from quiz_api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('quiz_api.urls')),
    path('auth/', include('accounts.urls')),

    path('', views.index),
    path('dashboard/', views.DashboardView, name="dashboard"),
    path('dashboard/principal/', views.principal_page),
    path('dashboard/teacher/', views.teacher_page),
    path('dashboard/student/', views.student_page),
]

handler404 = 'quiz_api.views.custom_404'
handler500 = 'quiz_api.views.custom_500'

