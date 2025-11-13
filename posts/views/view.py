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


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def feed(request):

    limit = int(request.GET.get("limit", 10))
    cursor = request.GET.get("cursor", None)

    # Newest first
    queryset = Post.objects.order_by("-id")

    if cursor:
        queryset = queryset.filter(id__lt=cursor)

    # Convert to list so negative indexing works
    posts = list(queryset[:limit])

    serializer = PostSerializer(posts, many=True)

    next_cursor = posts[-1].id if posts else None

    return Response({
        "results": serializer.data,
        "next_cursor": next_cursor
    })


urlpatterns = [
    path('<int:post_id>', view_post),
    path('feed', feed)
]