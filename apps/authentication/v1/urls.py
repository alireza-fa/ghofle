from django.urls import path

from apps.authentication.v1.views import token, sign_user


app_name = "auth_v1"

urlpatterns = [
    # sign
    path("login/", sign_user.LoginByPhoneNumberView.as_view(), name="login_by_phone_number"),
    path("verify/", sign_user.VerifySignUserView.as_view(), name="verify"),
    # path("login-by-password/", sign_user.UserLoginByPasswordView.as_view()),
    path("register/", sign_user.RegisterView.as_view(), name="register"),
    # token
    path("token/verify/", token.VerifyTokenView.as_view(), name="verify_token"),
    path("token/refresh/", token.RefreshAccessToken.as_view(), name="refresh_access_token"),
    path("token/ban/", token.BanRefreshTokenView.as_view(), name="ban_refresh_token"),
]
