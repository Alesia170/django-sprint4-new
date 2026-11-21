from django.contrib import admin

from blog.models import Category, Comment, Location, Post


class BaseAdmin(admin.ModelAdmin):
    list_display = ['is_published']
    list_filter = ['is_published']


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ['title', 'description', 'slug'] + BaseAdmin.list_display


@admin.register(Location)
class LocationAdmin(BaseAdmin):
    list_display = ['name'] + BaseAdmin.list_display


@admin.register(Post)
class PostAdmin(BaseAdmin):
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'title',
                    'pub_date',
                    'author',
                    'is_published',
                )
            },
        ),
        (
            'Дополнительно',
            {
                'fields': (
                    'category',
                    'location',
                    'image_tag',
                )
            },
        ),
    )
    readonly_fields = ('image_tag',)
    list_display = [
        'title',
        'pub_date',
        'author',
        'image_tag',
    ] + BaseAdmin.list_display
    list_filter = BaseAdmin.list_filter + ['category']


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    list_display = ['post', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username']
