"""
This file is used for creating custom user manager for the correspondent custom user.
"""
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Class for creating custom manager for managing custom user.
    """

    def create_user(self, email=None, first_name=None, last_name=None, password=None, **extra_fields):
        """
        Function for creating user w.r.t custom user.
        """
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = False
        user.is_active = True
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, email, password, last_name):
        """
        Function for creating superuser.
        """
        user = self.create_user(
            email,
            first_name,
            last_name,
            password,
        )
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_full_name(self):
        """
        Function to get full name.
        """
        fullname = "%s %s" % (self.first_name, self.last_name)
        return fullname.strip()

    def get_short_name(self):
        """
        Function to get short name.
        """
        return self.first_name
