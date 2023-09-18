from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from users.forms import CustomUserRegisterForm, CustomAuthenticationForm, CustomUserChangeForm, CustomPasswordResetForm, \
    CustomResetConfirmForm
from users.models import User


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('blog:home')

    def get_object(self, queryset=None):
        return self.request.user


class RegisterView(CreateView):
    model = User
    form_class = CustomUserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        return response


def verify_account(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    user.is_active = True
    user.save()
    login(request, user)
    return redirect(to=reverse('users:login'))


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        uid, token = form.save(self.request)
        return redirect('users:password_reset_confirm', uidb64=uid, token=token)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomResetConfirmForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
