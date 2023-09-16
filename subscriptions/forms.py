from django import forms
from django.utils import timezone

from blog.forms import StyleFormMixin
from subscriptions.models import Subscription


class SubscriptionForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Subscription
        fields = []  # Поля для выбора контента и платежа

    def create_subscription(self, user, blog):
        subscription = self.save(commit=False)
        subscription.user = user
        subscription.blog = blog
        subscription.status = True
        subscription.payment_status = True
        subscription.payment_date = timezone.now()
        subscription.save()
