from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser

from utilities import messages
from .managers import CustomUserManager
from utilities.mixins import (
    UserDetailModelMixin,
)


class CustomUser(AbstractBaseUser, PermissionsMixin, UserDetailModelMixin):
    """
    Class for creating model for storing users data.
    """

    email = models.EmailField(_("email address"), unique=True, error_messages={"unique": messages.EMAIL_ALREADY_ASSOCIATED})
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    updated_at = models.DateTimeField(auto_now=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        """
        Function to return email.
        """
        return self.email

    def get_full_name(self):
        """
        Function to get full name.
        """
        fullname = "%s %s" % (self.first_name, self.last_name)
        # print(fullname)
        return fullname.strip()
