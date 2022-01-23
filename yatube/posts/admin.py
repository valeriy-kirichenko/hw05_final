from django.contrib import admin

from .models import Follow, Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    actions_on_bottom = True
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'text', 'created',)
    actions_on_bottom = True
    search_fields = ('text',)
    list_filter = ('created',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    actions_on_bottom = True
    search_fields = ('user',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
