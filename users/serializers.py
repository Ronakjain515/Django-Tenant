from rest_framework import serializers
from django.contrib.auth import authenticate

from customuser.models import CustomUser
from .models import (
    Roles,
    UserProfile,
)


class LoginSerializer(serializers.Serializer):
    """
    Class for authorizing user for correct login credentials.
    """

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    default_error_messages = {
        "inactive_account": "User account is {}.",
        "invalid_credentials": "Email address or password is invalid.",
        "wrong_platform": "You are not authorised to login this platform.",
    }

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def __init__(self, *args, **kwargs):
        """
        Constructor Function for initializing UserLoginSerializer.
        """
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        """
        Function for validating and returning the created instance
        based on the validated data of the user.
        """
        self.user = authenticate(username=attrs.pop("email"), password=attrs.pop("password"))
        if self.user:
            main_user = self.context["user"]

            if not (main_user.status in ["ACTIVE", "INVITED"]):
                raise serializers.ValidationError(self.error_messages["inactive_account"].format(main_user.status.title()))

            return attrs
        else:
            raise serializers.ValidationError(self.error_messages["invalid_credentials"])


class UserSignupSerializer(serializers.ModelSerializer):
    """
    Class to create serializer for user signup.
    """

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email", "password", "is_superuser")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, password):
        """
        Function for validating and returning the created instance
        based on the validated data of the user.
        """
        password_length = len(password)

        if not 8 <= password_length <= 15:
            raise serializers.ValidationError("Password length should be between 8 and 15.")
        return password

    def create(self, validated_data):
        if validated_data.get("is_superuser"):
            user = CustomUser.objects.create_superuser(
                email=validated_data.pop("email"),
                first_name=validated_data.pop("first_name"),
                last_name=validated_data.pop("last_name"),
                password=validated_data.pop("password"),
            )
        else:
            user = CustomUser.objects.create_user(
                email=validated_data.pop("email"),
                first_name=validated_data.pop("first_name"),
                last_name=validated_data.pop("last_name"),
                password=validated_data.pop("password"),
            )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Class to create serializer for main user.
    """

    class Meta:
        model = UserProfile
        fields = ("id", "custom_user", "role", "status", "created_by")


class DummyUserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer class for roles.
    """

    class Meta:
        model = Roles
        fields = ("id", "role_type", "role_name", "description", "permission_policy", "created_by", "updated_by")


class ClientCredSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    app_name = serializers.CharField(max_length=50, required=True, allow_null=False, allow_blank=False)
