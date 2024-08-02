from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

v1 = [
    path("auth/", include("apps.authentication.v1.urls")),
    path("accounts/", include("apps.accounts.v1.urls")),
]

urlpatterns = [
    path("v1/", include(v1)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger/', SpectacularSwaggerView.as_view(), name='swagger'),
    path('schema/', SpectacularRedocView.as_view(), name='redoc'),
]
