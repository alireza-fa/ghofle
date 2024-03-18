from django.contrib import admin

from .models import Padlock, File, PadLockUserAccess, PadLockUser


@admin.register(Padlock)
class PadlockAdmin(admin.ModelAdmin):
    pass


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
