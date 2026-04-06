from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name'
    )
    search_fields = (
        'first_name',
        'email'
    )


admin.site.register(User, UserAdmin)
