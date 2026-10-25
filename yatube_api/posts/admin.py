from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'pub_date', 'group')
    list_filter = ('pub_date', 'group')
    search_fields = ('text', 'author__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'author', 'post', 'created')
    search_fields = ('text', 'author__username')


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user__username', 'following__username')
