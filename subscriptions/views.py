import json

import stripe
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView, ListView, TemplateView, CreateView
from blog.models import Blog
from subscriptions.forms import SubscriptionForm

from subscriptions.models import Subscription
from users.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = "http://127.0.0.1:8000"


class BlogCheckoutPageView(TemplateView):
    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        context = super(BlogCheckoutPageView, self).get_context_data(**kwargs)
        context.update({
            "blog": blog,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionView(View):

    def post(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = self.request.user
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': blog.price * 100,
                            'product_data': {
                                'name': blog.title,
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + reverse('subscriptions:success', kwargs={'slug': blog.slug}),
                cancel_url=YOUR_DOMAIN + reverse('subscriptions:cancel'),
                metadata={'blog_slug': blog.slug, 'user_id': user.pk}
            )
        except Exception as e:
            return JsonResponse({'error': str(e)})

        return redirect(checkout_session.url, code=303)
class SubscriptionCreateView(CreateView):
    model = Subscription
    template_name = 'subscriptions/subscription_form.html'
    success_url = reverse_lazy('blog:home')
    form_class = SubscriptionForm
    def form_valid(self, form):
        # Получаем блог на основе slug из URL
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])

        # Создаем подписку
        form.create_subscription(self.request.user, blog)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        context['blog'] = blog
        return context

class SubscriptionDeleteView(DeleteView):
    model = Subscription
    template_name = 'subscriptions/subscription_confirm_delete.html'
    success_url = reverse_lazy('blog:home')

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), blog__slug=self.kwargs['slug'])


class SubscriptionListView(ListView):
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'  # Создайте шаблон для списка подписок

    def get_queryset(self):
        user = self.request.user

        subscribed_blog_ids = Subscription.objects.filter(user=user, status=True).values_list('blog__id', flat=True)
        subscribed_blogs = Blog.objects.filter(id__in=subscribed_blog_ids, published_on=True)

        user_blogs = Blog.objects.filter(user=user, published_on=True)

        # Add this line to include unpublished blogs for the owner
        user_unpublished_blogs = Blog.objects.filter(user=user, published_on=False)

        combined_blogs = (user_blogs | subscribed_blogs | user_unpublished_blogs).distinct()

        return combined_blogs

class CancelView(TemplateView):
    template_name = 'subscriptions/cancel.html'

class SuccessView(TemplateView):
    template_name = 'subscriptions/success.html'

    def get(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = self.request.user
        # Создаем подписку для пользователя и связываем с контентом (блогом)
        Subscription.objects.create(
            user=user,
            blog=blog,
            status=True,  # Активируем подписку сразу после оплаты
            payment_status=True,  # Отмечаем оплату как успешную
            payment_date=timezone.now()
        )
        return render(request, 'subscriptions/success.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object

        blog_slug = session["metadata"]["blog_slug"]  # Получаем blog_slug из метаданных
        user_id = session["metadata"]["user_id"]
        blog = Blog.objects.get(slug=blog_slug)
        user = User.objects.get(pk=user_id)

        Subscription.objects.create(
            user=user,
            blog=blog,
            status=True,
            payment_status=True,
            payment_date=timezone.now()
        )
        # Отправляем сообщение о подписке
        print(f"Payment succeeded for blog: {blog.title}. User phone: {request.user.phone}")

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(phone=req_json['phone'])
            blog_slug = req_json['blog_slug']  # Get the blog slug from the request data
            user = self.request.user
            blog = get_object_or_404(Blog, slug=blog_slug)


            intent = stripe.PaymentIntent.create(
                amount=blog.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "blog_slug": blog.slug,
                    "user_id": user.pk
                }
            )
            Subscription.objects.create(
                user=user,
                blog=blog,
                status=True,
                payment_status=True,
                payment_date=timezone.now()
            )

            # Выводим сообщение об успешной оплате
            messages.success(request, 'Оплата успешно проведена. Ваша подписка активирована!')

            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })
