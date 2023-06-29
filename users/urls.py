from django.urls import path

from .views import (
    LoginAPIView,
    LogoutAPIView,
    DummyUserSignup,
    TenantSetupAPIView,
    GenerateClientCredAPIView,
)

urlpatterns = [
    path("login", LoginAPIView.as_view(), name="login"),
    path("logout", LogoutAPIView.as_view(), name="logout"),

    path("tenantSetup", TenantSetupAPIView.as_view(), name="tenant-setup"),
    path("dummyUserSignup", DummyUserSignup.as_view(), name="dummy-user-signup"),
    path("generateClient", GenerateClientCredAPIView.as_view(), name="generate-client"),

]
