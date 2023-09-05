from django import forms

from blog.forms import StyleFormMixin
from subscriptions.models import Subscription


class SubscriptionForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['blog', 'payment']  # Поля для выбора контента и платежа
