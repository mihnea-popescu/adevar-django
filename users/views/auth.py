from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.serializers import UserSerializer, LoginSerializer
from users.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import re_path, path
from django.utils import timezone as django_timezone
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# from rest_framework.decorators import authentication_classes, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework_simplejwt.authentication import JWTAuthentication


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

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('login', login),
    re_path('signup', signup),
    # path("change-password/", change_password)
]