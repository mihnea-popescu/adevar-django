from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.serializers.user_serializer import UserSerializer
from rest_framework.response import Response


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserSerializer(instance=request.user)
    return Response({"user": serializer.data})


urlpatterns = [
    path("", get_profile),
]