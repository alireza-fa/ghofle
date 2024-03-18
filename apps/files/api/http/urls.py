from django.urls import path

from .views import owner_padlock


urlpatterns = [
    path("own/", owner_padlock.UserOwnPadlockList.as_view()),
    path("create/", owner_padlock.CreatePadlock.as_view()),
    path("update/", owner_padlock.UpdatePadlock.as_view()),
    path("delete/", owner_padlock.DeletePadlock.as_view()),
]
