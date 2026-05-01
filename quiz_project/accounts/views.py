from quiz_api.models import *
from .serializer import *
from quiz_api.services import get_token_for_user, send_reset_email, send_create_user_email

from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


import logging
logger = logging.getLogger(__name__)


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
   
    def create(self, request: Request, *args: tuple, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        logger.info(f"Register successfully with email")
        return Response(
            {
                "message": "Account created successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "auth/forms.html")

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(request, username=email, password=password)

            if not user:
                logger.warning(f"Invalid email {email} or password")
                return Response(
                    {'error': 'Invalid email or password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            if not user.is_approved:
                logger.warning("user not approved")
                return Response(
                    {'error': 'User is not approve yet.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            tokens = get_token_for_user(user)

            logger.info(f"Successfully login with {email}")
            return Response({
                    "tokens": tokens,
                    "redirect": "/dashboard/",
                    'success': True,
                    'message': 'Login Successfull, Redirecting to dashboard...'
                }, status=status.HTTP_200_OK
            )
        
        logger.error(f"Invalid credentials {serializer.errors}")
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def LogoutView(request: HttpRequest) -> HttpResponse:
    logout(request)
    request.session.flush() 
    return redirect('login_user')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def PasswordRequestSentDoneView(request: Request) -> Response: 
    logger.info("Sent message")   
    return Response({'message': 'message sent'})


class RequestPasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        email = request.data.get('email')
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # 1. Generate UID and Token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # 2. Create url path 
            reset_url = f"{settings.PASSWORD_RESET_BASE_URL}/{uid}/{token}/"

            # 3. send mail
            try:
                send_reset_email(user.email, reset_url)
            except Exception as e:
                logger.error(f"Email failed: {str(e)}")
                return Response({
                    'error': 'Email sending failed'
                }, status=500)

            logger.info("Reset Link send to your email")
            return Response({
                'message': 'If this email exists, a reset link has been sent'
            }, status=200)
        
        logger.error("Check your your email")
        return Response({'error': 'Check Your Email'}, status=404)


class ResetPasswordAPIView(APIView):
    permission_classes =[permissions.AllowAny]

    def get(self, request: Request, uidb64: str, token: str) -> Response:
        return render(request, "auth/reset_password.html", {
            "uid": uidb64,
            "token": token
        })

    def post(self, request: Request, uidb64: str, token: str) -> Response:
        # decode the UID and check user
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (ValueError, OverflowError, TypeError, User.DoesNotExist):
            logger.warning("Token not found") 
            return Response({'error': 'Invalid user'}, status=400)

        is_valid = default_token_generator.check_token(user, token)

        # check valid token and valid user
        if user and is_valid:
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if new_password != confirm_password:
                logger.warning("Passwords do not match") 
                return Response({"error": "Passwords do not match"}, status=400)

            user.set_password(new_password)
            user.save()

            logger.info("Password reset succesfully.") 
            return Response({
                'message': 'Password reset succesfully.',
                'success': True
            })
        logger.error('The reset link is in valid or expire')        
        return Response({
            'error': 'The reset link is in valid or expired token.'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request: Request) -> Response:
        profile, _ = Profile.objects.get_or_create(user=request.user)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'message': 'Profile data updated succefully',
            'data': serializer.data
        }, status=200)

