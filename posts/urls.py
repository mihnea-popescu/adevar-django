from django.urls import path, include

urlpatterns = [
    path("create/", include("posts.views.create")),
    path("view/", include("posts.views.view")),
]