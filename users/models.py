from django.db import models
from utilities.constants import (
    ROLE_TYPE_MODEL_CHOICES,
    USER_STATUS_MODEL_CHOICES,
)
from .managers import ClientCredManager
from customuser.models import CustomUser
from utilities.mixins import CustomModelMixin


class Roles(CustomModelMixin):
    """
    Class for creating model for roles and its permissions.
    """

    role_type = models.CharField(max_length=50, null=False, blank=False, choices=ROLE_TYPE_MODEL_CHOICES)
    role_name = models.CharField(max_length=200, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    permission_policy = models.JSONField(null=False, blank=False)


class UserProfile(models.Model):
    """
    Class for creating model for storing users data.
    """

    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False, blank=False, related_name="custom_user")
    role = models.ForeignKey(Roles, null=True, blank=False, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=USER_STATUS_MODEL_CHOICES)
    created_by = models.ForeignKey("self", null=True, blank=False, on_delete=models.CASCADE, related_name="created_by_%(class)s")


class OAuthClientCreds(models.Model):
    """
    Class for creating model for storing OAuth client credentials.
    """

    client_id = models.CharField(max_length=200, null=False, blank=False)
    client_secret = models.CharField(max_length=300, null=False, blank=False)

    objects = ClientCredManager()
