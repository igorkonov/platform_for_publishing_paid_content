from django.urls import path
from django.views.decorators.cache import cache_page

from subscriptions.apps import SubscriptionsConfig
from subscriptions.views import SubscriptionDeleteView, SubscriptionListView, CancelView, \
    SuccessView, CreateCheckoutSessionView, BlogCheckoutPageView, StripeIntentView, stripe_webhook, \
    SubscriptionCreateView

app_name = SubscriptionsConfig.name


urlpatterns = [
    path('subscription-create/<slug:slug>/', SubscriptionCreateView.as_view(), name='subscription_create'),
    path('subscription-cancel/<slug:slug>/', SubscriptionDeleteView.as_view(), name='subscription_delete'),
    path('subscription-list/', cache_page(60)(SubscriptionListView.as_view()), name='subscription_list'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/<slug:slug>/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<slug:slug>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('', BlogCheckoutPageView.as_view(), name='checkout-page'),
    path('create-payment-intent/<int:pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]
