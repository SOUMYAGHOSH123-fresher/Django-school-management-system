from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'principal'

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsTeacherOrStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'student' or request.user.role == 'teacher')


class IsPrincipalOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'principal' or request.user.role == 'teacher')


class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user

    