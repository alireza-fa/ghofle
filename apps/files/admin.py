from django.contrib import admin

from .models import Padlock, File, PadLockUserAccess, PadLockUser


class PadlockUserInline(admin.TabularInline):
    model = PadLockUser


@admin.register(Padlock)
class PadlockAdmin(admin.ModelAdmin):
    inlines = (PadlockUserInline,)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    pass
