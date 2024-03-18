from django.contrib import admin

from .models import ProfileUser


@admin.register(ProfileUser)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "name", "surname", "phone", "email", "avatar")
    list_display_links = "pk", "user"
    ordering = ("pk",)
    search_fields = ("name",)
