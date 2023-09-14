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
from django.views.generic import DeleteView, ListView, TemplateView
from blog.models import Blog

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


class SubscriptionDeleteView(DeleteView):
    model = Subscription
    template_name = 'subscriptions/subscription_confirm_delete.html'
    success_url = reverse_lazy('blog:home')

    def get_queryset(self):
        # Фильтруем подписки, чтобы пользователь мог отменить только свою подписку
        return Subscription.objects.filter(user=self.request.user)


class SubscriptionListView(ListView):
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'  # Создайте шаблон для списка подписок

    def get_queryset(self):
        # Get the user object
        user = self.request.user

        # Get a list of blog IDs that the user has subscribed to
        subscribed_blog_ids = Subscription.objects.filter(user=user, status=True).values_list('blog__id', flat=True)

        # Get the blogs associated with the subscriptions
        subscribed_blogs = Blog.objects.filter(id__in=subscribed_blog_ids, published_on=True)

        # Get the user's own blogs
        user_blogs = Blog.objects.filter(user=user, published_on=True)

        # Combine the two querysets
        combined_blogs = user_blogs | subscribed_blogs

        return combined_blogs.distinct()

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
