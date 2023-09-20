from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


class UserCreationForm(forms.ModelForm):
    """
        Форма для создания нового пользователя в админке.

        Attributes:
            password (CharField): Поле для пароля.
            confirm_password (CharField): Поле для подтверждения пароля.
    """
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'username',
            'phone',
            'avatar',
        )

    def clean_confirm_password(self):
        """
            Проверяет, совпадают ли пароли.

            Returns:
                str: Подтвержденный пароль.

            Raises:
                forms.ValidationError: Если пароли не совпадают.
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        """
            Сохраняет пользователя.

            Args:
                commit (bool, optional): Флаг сохранения. По умолчанию True.

            Returns:
                User: Сохраненный пользователь.
        """

        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    """
        Администратор пользователей.

        Attributes:
            form (UserChangeForm): Форма изменения пользователя.
            add_form (UserCreationForm): Форма создания пользователя.
            list_display (tuple): Отображаемые поля в списке.
            fieldsets (tuple): Набор полей.
            add_fieldsets (tuple): Набор полей для создания.
            search_fields (tuple): Поля для поиска.
            ordering (tuple): Поля для сортировки.
            filter_horizontal (tuple): Поля для фильтрации.
    """

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'phone', 'avatar',)
    fieldsets = (
        (None, {'fields': (
            'password', 'username', 'phone', 'avatar')}),
        ('Права доступа', {'fields': ('is_superuser', 'is_staff', 'is_active', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'password', 'confirm_password', 'username', 'phone', 'avatar',)}),

        ('Права доступа', {'fields': ('is_superuser', 'is_staff', 'is_active', 'user_permissions')}),
    )
    search_fields = ('username', 'phone',)
    ordering = ('id', 'phone',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
