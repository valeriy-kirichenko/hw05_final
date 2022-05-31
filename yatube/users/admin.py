from django.contrib import admin

from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar', 'about')
    actions_on_bottom = True
    search_fields = ('user',)


admin.site.register(UserProfile, UserProfileAdmin)
