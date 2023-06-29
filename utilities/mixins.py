from django.db import models
from django.utils import timezone


class UserDetailModelMixin(models.Model):
    """
    Mixin class for creating user details.
    """

    first_name = models.CharField(max_length=30, null=False, blank=False)
    last_name = models.CharField(max_length=30, null=False, blank=False)

    class Meta:
        abstract = True


class CustomModelMixin(models.Model):
    """
    Mixin class for creating util details.
    """

    is_deleted = models.BooleanField(null=False, blank=False, default=False)
    created_by = models.ForeignKey("users.UserProfile", null=False, blank=False, on_delete=models.CASCADE, related_name="created_by_%(class)s")
    updated_by = models.ForeignKey("users.UserProfile", null=False, blank=False, on_delete=models.CASCADE, related_name="updated_by_%(class)s")
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        abstract = True
