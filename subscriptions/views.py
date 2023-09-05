from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from subscriptions.forms import SubscriptionForm
from subscriptions.models import Subscription


class SubscriptionCreateView(CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscription/subscription_form.html'  # Создайте шаблон для формы подписки
    success_url = '/subscription/list/'  # Перенаправляем пользователя на список подписок после успешной подписки

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = True  # Устанавливаем статус подписки
        return super().form_valid(form)


class SubscriptionDeleteView(DeleteView):
    model = Subscription
    template_name = 'subscription/subscription_confirm_delete.html'  # Создайте шаблон для подтверждения отмены подписки
    success_url = reverse_lazy('subscription_list')

    def get_queryset(self):
        # Фильтруем подписки, чтобы пользователь мог отменить только свою подписку
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionListView(ListView):
    model = Subscription
    template_name = 'subscription/subscription_list.html'  # Создайте шаблон для списка подписок

    def get_queryset(self):
        # Отображаем только подписки текущего пользователя
        return Subscription.objects.filter(user=self.request.user)
