from django.contrib.auth import get_user_model

User = get_user_model()


def get_profile_user(user_id: int) -> User:
    profile = User.objects.prefetch_related("own_padlocks", "padlock_accesses", "padlocks").get(id=user_id)

    return profile
