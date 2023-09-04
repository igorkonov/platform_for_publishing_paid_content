from django import forms
from django.contrib.auth.forms import UsernameField, UserChangeForm, UserCreationForm, AuthenticationForm
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
    class Meta:
        model = User
        fields = ('phone', 'password1', 'password2')
        field_classes = {'username': UsernameField}


class CustomAuthenticationForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = User

    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )