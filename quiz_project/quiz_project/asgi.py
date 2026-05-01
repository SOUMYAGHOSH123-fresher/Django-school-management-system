"""
ASGI config for quiz_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_project.settings')

application = get_asgi_application()





#  // ✅ Role-based redirect
#         <!-- if (user.role === "principal") {
#             window.location.href = "/dashboard/";
#         }
#         else if (user.role === "teacher") {
#             window.location.href = "/dashboard/";
#         }
#         else if (user.role === "student") {
#             window.location.href = "/dashboard/";
#         } 
