from django.db import models
from django.utils import timezone as django_timezone


class AppQuerySet(models.QuerySet):
    def delete(self):
        now = django_timezone.now()
        self.update(is_deleted=True, updated_at=now)

    def update(self, **kwargs):
        """Ensure that `updated_at` is automatically updated on bulk updates."""
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = django_timezone.now()  # Automatically update the updated_at field
        return super().update(**kwargs)


class AppManager(models.Manager):
    def get_queryset(self):
        return models.QuerySet(self.model, using=self._db).exclude(is_deleted=True)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    is_deleted = models.BooleanField(default=False)

    def delete(self):
        """Mark the record as deleted instead of deleting it"""

        self.is_deleted = True
        self.save()

    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(default=django_timezone.now)

    def save(self, *args, **kwargs):
        """Override save method to update last_activity timestamp."""
        self.updated_at = django_timezone.now()  # Ensure updated_at is also updated
        super().save(*args, **kwargs)

    objects = AppManager()