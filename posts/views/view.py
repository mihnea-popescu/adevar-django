from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from posts.models.Post import Post
from posts.serializers.PostSerializer import PostSerializer
from django.urls import path
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def view_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    serializer = PostSerializer(post)

    return Response({"post": serializer.data})


urlpatterns = [
    path('<int:post_id>', view_post),
]