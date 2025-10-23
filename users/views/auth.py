from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializers import UserSerializer, LoginSerializer, ChangePasswordSerializer, ResetPasswordRequestSerializer, ResetPasswordSerializer
from users.models import User, PasswordReset
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import re_path, path
from django.utils import timezone as django_timezone
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import timedelta
from users.tasks.send_reset_password_token import send_reset_password_email
from django.shortcuts import render



@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    user = get_object_or_404(User, email=data['email'])
    if not user.check_password(data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    user.last_login = django_timezone.now()

    if 'language_tag' in data and data['language_tag']:
        user.language_tag = data['language_tag']

    if 'country_code' in data and data['country_code']:
        user.country_code = data['country_code']

    if 'timezone' in data and data['timezone']:
        user.timezone = data['timezone']

    user.save()

    serializer = UserSerializer(instance=user)
    return Response({"user": serializer.data})


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        if request.data['email'] and User.objects.filter(email=request.data['email']).exists():
            return Response({"email": ["An account with this email already exists."]}, status=400)

        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.username = user.generate_username_from_email(request.data['email'])
        user.set_password(request.data['password'])
        user.last_login = django_timezone.now()
        user.save()

        read_serializer = UserSerializer(instance=user)

        return Response({"user": read_serializer.data})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        user = request.user

        if not user.check_password(data['password']):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(data['new_password'])
        user.save()

        return Response({'success': True})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    serializer = ResetPasswordRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    user = User.objects.filter(email__iexact=email).first()

    if user:
        if user.last_change_password_email_sent_at and user.last_change_password_email_sent_at > django_timezone.now() - timedelta(
                minutes=10):
            # sent within the last 5 minutes
            return Response({'success': True}, status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        reset = PasswordReset(email=email, token=token)
        reset.save()

        # Update user last validation email sent at
        user.last_change_password_email_sent_at = django_timezone.now()
        user.save()

        # send_reset_password_email.delay(user.id, token)
        send_reset_password_email(user.id, token)

    return Response({'success': True}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reset_password(request, token):
    if request.method == 'GET':
        email = request.query_params.get('email')

        if not email:
            return render(request, "password_reset/invalid.html", {
                "error": "Missing email parameter."
            })
        reset_obj = PasswordReset.objects.filter(token=token, email=email).first()
        # GET
        if not reset_obj or reset_obj.created_at < django_timezone.now() - timedelta(minutes=60):
            return render(request, "password_reset/invalid.html")
        return render(request, "password_reset/form.html", {"token": token, "email": reset_obj.email})

    # POST
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data

    reset_obj = PasswordReset.objects.filter(token=token, email=data['email']).first()
    if not reset_obj:
        return Response({"details": "Invalid token"},
                        status=status.HTTP_400_BAD_REQUEST)

    if reset_obj.created_at < django_timezone.now() - timedelta(minutes=60):
        return Response({"details": "Expired token"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email=reset_obj.email).first()

    if user:
        user.set_password(data['new_password'])
        user.save()

        reset_obj.delete()

        return Response({'success': True})
    else:
        return Response({'details': 'No user found'}, status=404)



urlpatterns = [
    re_path('login/', login),
    re_path('signup/', signup),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("change-password/", change_password),
    path('reset-password/', request_password_reset),
    path("reset-password/<str:token>/", reset_password),
]