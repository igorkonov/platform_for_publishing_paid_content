from django.contrib import admin
from blog.forms import BlogAdminForm
from blog.models import Blog, Comment


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
        Административное представление для модели Blog.

        Определены следующие атрибуты:
            - list_display: Поля, отображаемые в списке записей модели.
            - prepopulated_fields: Поля, автоматически заполняемые при создании записи.
            - form: Форма, используемая для администрирования записей.

        Определено действие republish для пакетного обновления поля published_on.
    """
    list_display = ('id', 'title', 'slug', 'description', 'image', 'published_on', 'user', 'price',)
    prepopulated_fields = {"slug": ("title",)}
    form = BlogAdminForm

    def republish(self, request, queryset):
        """
            Действие повторной публикации выбранных записей.

            Args:
                request (HttpRequest): Запрос от администратора.
                queryset (QuerySet): Выборка записей для публикации.

            Returns:
                None
        """
        queryset.update(published_on=True)
        self.message_user(request, "Выбранные записи были переизданы")

    republish.short_description = "Повторная публикация выбранных записей"
    actions = [republish]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
        Административное представление для модели Comment.
        Определено поле list_display для отображения в списке записей модели.
    """
    list_display = ('id', 'comment', 'user',)
