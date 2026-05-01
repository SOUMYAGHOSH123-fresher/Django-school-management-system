from django.contrib import admin
from quiz_api.models import User, Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'subject', 'student_class', 'role', 'is_approved']

admin.site.register(Profile)
