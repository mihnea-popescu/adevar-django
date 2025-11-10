from django.urls import path, include

urlpatterns = [
    path("create/", include("posts.views.create")),
]