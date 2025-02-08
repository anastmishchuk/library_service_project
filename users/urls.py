from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from users.views import CreateUserView, ManageUserView

urlpatterns = [
    path("users/", CreateUserView.as_view(), name="create"),
    path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("users/me/", ManageUserView.as_view(), name="manage"),
]

app_name = "users"
