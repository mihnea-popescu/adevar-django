from django.urls import path, include

urlpatterns = [
    path("auth/", include("users.views.auth")),
    path("user/", include("users.views.user"))
]