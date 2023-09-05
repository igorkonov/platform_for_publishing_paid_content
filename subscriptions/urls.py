from django.urls import path

from subscriptions.apps import SubscriptionsConfig
from subscriptions.views import SubscriptionCreateView, SubscriptionDeleteView, SubscriptionListView

app_name = SubscriptionsConfig.name


urlpatterns = [
    path('subscription/create/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('subscription/cancel/<int:pk>/', SubscriptionDeleteView.as_view(), name='subscription_delete'),
    path('subscription/list/', SubscriptionListView.as_view(), name='subscription_list'),
]