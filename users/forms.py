from django import forms
from django.contrib.auth.forms import UsernameField, UserChangeForm, UserCreationForm, AuthenticationForm, \
    PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from blog.forms import StyleFormMixin
from users.models import User


class CustomUserChangeForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ('phone', 'avatar')
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()


class CustomUserRegisterForm(StyleFormMixin, UserCreationForm):
    phone = forms.CharField(
        max_length=25,
        required=True,
        label="Номер телефона",
        widget=forms.TextInput(attrs={'placeholder': 'Номер телефона'}),
    )

    class Meta:
        model = User
        fields = ('phone', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером уже существует")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = User

    username = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True}),
        max_length=254,
        required=True,
        label=_("Номер телефона"),
    )


class CustomPasswordResetForm(StyleFormMixin, PasswordResetForm):
    email = forms.EmailField(  # Оставьте это поле, но скройте его в форме
        widget=forms.HiddenInput(),
        required=False,  # Сделайте его необязательным
    )

    phone = forms.CharField(
        label=_("Номер телефона"),
        max_length=254,
        widget=forms.TextInput(attrs={"autocomplete": "phone"}),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким номером не найден")
        return phone

    def save(self, request, **kwargs):
        phone = self.cleaned_data["phone"]
        user = User.objects.get(phone=phone)

        # Генерируем токен сброса пароля
        token_generator = kwargs.get('token_generator', default_token_generator)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        return uid, token


class CustomResetConfirmForm(SetPasswordForm):
    class Meta:
        model = User
