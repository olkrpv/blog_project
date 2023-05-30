from django.contrib import admin

from .models import Category, Comment, Location, Post


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title', 'description', 'slug',
        'created_at', 'is_published',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'slug')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_published')
    list_editable = ('is_published',)
    search_fields = ('name',)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category',
        'location', 'created_at', 'is_published',
    )
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('author', 'category', 'location')
    empty_value_display = 'Не задано'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'post', 'created_at', 'author'
    )
    search_fields = ('text',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
