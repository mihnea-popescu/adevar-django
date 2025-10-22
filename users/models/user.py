from __future__ import annotations

from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager as DjangoUserManager
from django.utils import timezone as django_timezone

from core.time.timezones import get_local_time
import random
import string


class UserQuerySet(models.QuerySet):
    def update(self, **kwargs):
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = django_timezone.now()
        return super().update(**kwargs)


class UserManager(DjangoUserManager.from_queryset(UserQuerySet)):
    def update_last_activity(self, user: User) -> int:
        now: datetime = django_timezone.now()
        return self.filter(id=user.id).update(last_activity=now)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True, unique=True, default=None)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)

    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    is_staff = models.BooleanField(default=False)

    language_tag = models.CharField(max_length=32, blank=True, null=True)
    country_code = models.CharField(max_length=8, blank=True, null=True)
    timezone = models.SmallIntegerField(default=0, help_text="Most recent timezone used by the user")

    last_activity = models.DateTimeField(default=django_timezone.now)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(default=django_timezone.now)
    last_change_password_email_sent_at = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.phone_number or self.username

    def generate_username_from_email(self, email: str) -> str:
        """
        Generate a unique username based on the user's email address.
        Example:
            "mihnea@example.com" → "mihnea"
            If "mihnea" already exists → "mihnea_3k7"
        """
        # Extract the part before @
        base_username = email.split("@")[0].lower()

        # Remove invalid characters just in case
        base_username = "".join(ch for ch in base_username if ch.isalnum() or ch in ("_", "."))

        # If username exists, append random 3-char suffix
        username = base_username
        while User.objects.filter(username=username).exists():
            suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
            username = f"{base_username}_{suffix}"

        return username

    def save(self, *args, **kwargs):
        self.last_activity = django_timezone.now()
        self.updated_at = django_timezone.now()
        super().save(*args, **kwargs)

    def to_dict(self) -> dict:
        fields_to_get = ["id", "username", "first_name", "last_name"]
        return {field: getattr(self, field) for field in fields_to_get}

    def local_time(self, utc_time: datetime) -> datetime:
        return get_local_time(utc_time, self.timezone) if self.timezone else utc_time