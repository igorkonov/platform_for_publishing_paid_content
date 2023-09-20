from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from users.forms import CustomUserRegisterForm, CustomAuthenticationForm, CustomUserChangeForm, CustomPasswordResetForm, \
    CustomResetConfirmForm
from users.models import User


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
        Контроллер для обновления профиля пользователя.

        Attributes:
            model (User): Модель пользователя.
            form_class (CustomUserChangeForm): Переопределенная форма для изменения данных пользователя.
            success_url (str): URL, на который будет перенаправлен пользователь после успешного обновления профиля.
    """

    model = User
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('blog:home')

    def get_object(self, queryset=None):
        """
            Получает объект пользователя.
        """
        return self.request.user


class RegisterView(CreateView):
    """
       Контроллер для регистрации нового пользователя.

       Attributes:
           model (User): Модель пользователя.
           form_class (CustomUserRegisterForm): Переопределенная форма для регистрации.
           success_url (str): URL, на который будет перенаправлен пользователь после успешной регистрации.
    """

    model = User
    form_class = CustomUserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """
            Обработчик успешной регистрации.
        """

        response = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        return response


def verify_account(request, user_pk):
    """
        Подтверждение аккаунта пользователя.

        Args:
            request: Запрос.
            user_pk (int): Идентификатор пользователя.

        Returns:
            HttpResponse: HTTP-ответ.
    """

    user = get_object_or_404(User, pk=user_pk)
    user.is_active = True
    user.save()
    login(request, user)
    return redirect(to=reverse('users:login'))


class CustomLoginView(LoginView):
    """
        Переопределенный контроллер для входа в систему.
    """

    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class CustomPasswordResetView(PasswordResetView):
    """
        Переопределенный контроллер для сброса пароля.
    """

    template_name = 'users/password_reset_form.html'
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        """
            Обработчик успешного сброса пароля.
        """

        uid, token = form.save(self.request)
        return redirect('users:password_reset_confirm', uidb64=uid, token=token)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
        Переопределенный контроллер для подтверждения сброса пароля.
    """

    form_class = CustomResetConfirmForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
        Переопределенный контроллер для успешного сброса пароля.
    """
    template_name = 'users/password_reset_complete.html'
