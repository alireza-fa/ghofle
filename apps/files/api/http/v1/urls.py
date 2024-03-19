from django.urls import path

from .views import owner_padlock

urlpatterns = [
    path("own/", owner_padlock.UserOwnPadlockListView.as_view()),
    path("create/", owner_padlock.CreatePadlockView.as_view()),
    path("delete/<int:padlock_id>/", owner_padlock.DeletePadlockView.as_view()),
]
