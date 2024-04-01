from django.urls import path, include

v1 = [
    path("auth/", include("apps.authentication.api.http.v1.urls")),
    path("padlocks/", include("apps.files.api.http.v1.urls")),
    path("finance/", include("apps.finance.api.http.v1.urls")),
    path("accounts/", include("apps.accounts.api.http.v1.urls")),
]

urlpatterns = [
    path("v1/", include(v1))
]
