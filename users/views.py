import json
from rest_framework import status
from django.db import transaction
from rest_framework.generics import (
    CreateAPIView,
)
from oauthlib.oauth2 import OAuth2Error
from tenants.models import Client, Domain
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.models import get_application_model
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from utilities import (
    messages,
)
from .models import (
    OAuthClientCreds,
)
from .serializers import (
    LoginSerializer,
    ClientCredSerializer,
    UserSignupSerializer,
    UserProfileSerializer,
    DummyUserRoleSerializer,
)
from utilities.utils import (
    ResponseInfo,
)
from customuser.models import CustomUser


class LoginAPIView(OAuthLibCore, CreateAPIView):
    """
    Class for creating api for Login users.
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        """
        Constructor function for formatting the web response to return.
        """
        self.response_format = ResponseInfo().response
        super(LoginAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST method for login user.
        """
        try:
            email = request.data.get("email")
            if email:
                user = CustomUser.objects.get(email=email)
                main_user = user.custom_user.get()
                user_type = request.data.get("role")

                if user_type:
                    user_serializer = self.get_serializer(
                        data=request.data,
                        context={
                            "role": user_type,
                            "user": main_user,
                        },
                    )

                    if user_serializer.is_valid(raise_exception=True):
                        client_id, client_secret = OAuthClientCreds.objects.load_data()
                        uri, http_method, body, headers = self._extract_params(request)
                        body = (
                            "username="
                            + email
                            + "&password="
                            + request.data["password"]
                            + "&grant_type=password"
                            + "&client_id="
                            + client_id
                            + "&client_secret="
                            + client_secret
                        )
                        extra_credentials = self._get_extra_credentials(request)

                        try:
                            headers, body, response_status = self.server.create_token_response(uri, http_method, body, headers, extra_credentials)
                            body = json.loads(body)
                            if response_status == 200:
                                if main_user.status == "INVITED":
                                    main_user.status = "ACTIVE"
                                    main_user.save()
                                response_data = {
                                    "token": body,
                                    "email": user.email,
                                    "first_name": user.first_name,
                                    "last_name": user.last_name,
                                }
                                self.response_format["data"] = response_data
                            else:
                                self.response_format["data"] = None
                                self.response_format["error"] = "error"
                                self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                                self.response_format["message"] = [body["error"]]
                        except OAuth2Error as exc:
                            self.response_format["data"] = None
                            self.response_format["error"] = "error"
                            self.response_format["status_code"] = exc.status_code
                            self.response_format["message"] = [json.loads(exc.json)["error_description"]]
                else:
                    self.response_format["data"] = None
                    self.response_format["error"] = "role"
                    self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                    self.response_format["message"] = [messages.THIS_FIELD_REQUIRED]
            else:
                self.response_format["data"] = None
                self.response_format["error"] = "email"
                self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                self.response_format["message"] = [messages.THIS_FIELD_REQUIRED]
        except CustomUser.DoesNotExist:
            self.response_format["data"] = None
            self.response_format["error"] = "user"
            self.response_format["status_code"] = status.HTTP_404_NOT_FOUND
            self.response_format["message"] = [messages.DOES_NOT_EXIST.format("User")]
        return Response(self.response_format)


class LogoutAPIView(OAuthLibCore, CreateAPIView):
    """
    Class for creating API view for user logout.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (OAuth2Authentication,)
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        """
        Constructor function for formatting the web response to return.
        """
        self.response_format = ResponseInfo().response
        super(LogoutAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST Method for logging out the user and blacklisting the access token used.
        """
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if auth_header:
            key, access_token = auth_header.split(" ")
            if key == "Bearer":
                uri, http_method, body, headers = self._extract_params(request)
                client_id, client_secret = OAuthClientCreds.objects.load_data()
                body = (
                    "client_id=" + client_id + "&client_secret=" + client_secret + "&token=" + access_token
                )

                try:
                    headers, body, response_status = self.server.create_revocation_response(uri, http_method, body, headers)

                    if response_status == 200:
                        self.response_format["message"] = [messages.LOGOUT_SUCCESS]
                        self.response_format["data"] = None

                except OAuth2Error as exc:
                    self.response_format["data"] = None
                    self.response_format["error"] = "error"
                    self.response_format["status_code"] = exc.status_code
                    self.response_format["message"] = [json.loads(exc.json)["error_description"]]
        return Response(self.response_format)


class TenantSetupAPIView(CreateAPIView):
    """
    Class for creating api for tenant setup.
    """

    authentication_classes = ()
    permission_classes = ()
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        """
        Constructor function for formatting the web response to return.
        """
        self.response_format = ResponseInfo().response
        super(TenantSetupAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        POST Method tenant setup.
        """
        # create your first real tenant
        tenant = Client(schema_name="tenant", name="Tenant Inc.")
        tenant.save()  # migrate_schemas automatically called, your tenant is ready to be used!

        # Add one or more domains for the tenant
        domain = Domain()
        domain.domain = "tenant"
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()

        return Response(self.response_format)


class DummyUserSignup(CreateAPIView):
    """
    Class for creating api for dummy user creation.
    """

    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSignupSerializer

    def __init__(self, **kwargs):
        """
        Constructor function for formatting the web response to return.
        """
        self.user = None
        self.main_user = None
        self.role = None
        self.response_format = ResponseInfo().response
        super(DummyUserSignup, self).__init__(**kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        POST method for creating dummy user.
        """

        user_serializer = self.get_serializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            self.user = user_serializer.save()

            if not request.data.get("is_shared_schema", False):
                main_user_data = {
                    "custom_user": self.user.id,
                    "role": None,
                    "status": "ACTIVE",
                    "created_by": None,
                }

                main_user_serializer = UserProfileSerializer(data=main_user_data)
                if main_user_serializer.is_valid(raise_exception=True):
                    self.main_user = main_user_serializer.save()
                    role_data = {
                        "role_type": request.data["role_type"],
                        "role_name": request.data["role_name"],
                        "description": request.data["role_description"],
                        "permission_policy": request.data["role_policy"],
                        "created_by": self.main_user.id,
                        "updated_by": self.main_user.id,
                    }
                    role_serializer = DummyUserRoleSerializer(data=role_data)
                    if role_serializer.is_valid(raise_exception=True):
                        self.role = role_serializer.save()

                self.main_user.role = self.role
                self.main_user.created_by = self.main_user
                self.main_user.save()

            self.response_format["data"] = user_serializer.data
            self.response_format["error"] = None
            self.response_format["status_code"] = status.HTTP_201_CREATED
            self.response_format["message"] = [messages.CREATED.format("User")]

            return Response(self.response_format)


class GenerateClientCredAPIView(CreateAPIView):
    """
    Class to create api to generate client creds.
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = ClientCredSerializer

    def __init__(self, **kwargs):
        """
        Constructor function for formatting web response to return.
        """
        self.response_format = ResponseInfo().response
        super(GenerateClientCredAPIView, self).__init__(**kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Post method for creating client creds.
        """
        client_serializer = self.get_serializer(data=request.data)
        if client_serializer.is_valid(raise_exception=True):
            try:
                user = CustomUser.objects.filter(is_superuser=True).first()

                application = get_application_model()
                app = application(
                    name=request.data.get("app_name", "dummy_app"), client_type="confidential", authorization_grant_type="password", user_id=user.id
                )

                client_id = app.client_id
                client_secret = app.client_secret

                app.save()

                OAuthClientCreds.objects.save_data(client_id=client_id, client_secret=client_secret)
                self.response_format["status_code"] = status.HTTP_201_CREATED
                self.response_format["data"] = None
                self.response_format["error"] = None
                self.response_format["message"] = [messages.CREATED.format("Client")]

            except CustomUser.DoesNotExist:
                self.response_format["status_code"] = status.HTTP_400_BAD_REQUEST
                self.response_format["data"] = None
                self.response_format["error"] = "User"
                self.response_format["message"] = [messages.DOES_NOT_EXIST.format("User")]

        return Response(self.response_format)
