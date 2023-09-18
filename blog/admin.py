from django.contrib import admin

from blog.forms import BlogAdminForm
from blog.models import Blog, Comment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'description', 'image', 'published_on', 'user', 'price',)
    prepopulated_fields = {"slug": ("title",)}
    form = BlogAdminForm

    def republish(self, request, queryset):
        queryset.update(published_on=True)
        self.message_user(request, "Выбранные записи были переизданы")

    republish.short_description = "Повторная публикация выбранных записей"
    actions = [republish]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'user',)
