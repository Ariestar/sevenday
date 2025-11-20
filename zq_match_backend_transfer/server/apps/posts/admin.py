from django.contrib import admin
from .models import Post, PostLike, PostComment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'team', 'task', 'create_time']
    list_filter = ['create_time', 'task']
    search_fields = ['title', 'description']
    readonly_fields = ['create_time', 'update_time']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'create_time']
    list_filter = ['create_time']
    search_fields = ['post__title', 'user__username']
    readonly_fields = ['create_time']


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'content', 'create_time']
    list_filter = ['create_time']
    search_fields = ['post__title', 'user__username', 'content']
    readonly_fields = ['create_time', 'update_time']
