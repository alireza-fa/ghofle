from django.urls import path

from apps.finance.api.http.v1.views import payment


urlpatterns = [
    path("verify/<int:track_id>/", payment.VerifyPayView.as_view()),
]
