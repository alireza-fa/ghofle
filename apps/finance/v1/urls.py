from django.urls import path

from apps.finance.v1.views import payment


urlpatterns = [
    path("verify/<int:track_id>/", payment.VerifyPayView.as_view()),
]
