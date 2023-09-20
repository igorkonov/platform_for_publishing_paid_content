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
    """
        Контроллер для страницы оформления подписки на блог.

        Attributes:
            template_name (str): Имя шаблона страницы оформления подписки.
    """

    template_name = "checkout.html"

    def get_context_data(self, **kwargs):
        """
            Получает данные контекста.

            Args:
                **kwargs: Дополнительные аргументы.

            Returns:
                dict: Словарь с данными контекста.
        """

        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        context = super(BlogCheckoutPageView, self).get_context_data(**kwargs)
        context.update({
            "blog": blog,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


class CreateCheckoutSessionView(View):
    """
        Контроллер для создания сессии оформления подписки.

        Methods:
            post(request, *args, **kwargs): Обрабатывает POST-запрос, создает сессию оформления подписки.
    """
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


class CancelView(TemplateView):
    """
        Контроллер для отмены подписки.

        Attributes:
            template_name (str): Имя шаблона страницы отмены подписки.
    """
    template_name = 'subscriptions/cancel.html'


class SuccessView(TemplateView):
    """
        Контроллер для успешной оплаты и активации подписки.

        Attributes:
            template_name (str): Имя шаблона страницы успешной оплаты и активации подписки.
        Methods:
            get(request, *args, **kwargs): Обрабатывает GET-запрос, активирует подписку.
    """

    template_name = 'subscriptions/success.html'

    def get(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = self.request.user

        # Создаем подписку для пользователя и связываем с контентом (блогом)
        Subscription.objects.create(
            user=user,
            blog=blog,
            status=True,
            payment_status=True,
            payment_date=timezone.now()
        )
        return render(request, 'subscriptions/success.html')


@csrf_exempt
def stripe_webhook(request):
    """
        Обработчик событий от Stripe.

        Args:
            request: Запрос события от Stripe.

        Returns:
            HttpResponse: Ответ.
    """

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

        blog_slug = session["metadata"]["blog_slug"]
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
    """
       Контроллер для создания намерения оплаты.

       Methods:
            post(request, *args, **kwargs): Обрабатывает POST-запрос, создает намерение оплаты.
    """
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(phone=req_json['phone'])
            blog_slug = req_json['blog_slug']
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
            return JsonResponse({'error': str(e)})


class SubscriptionCreateView(CreateView):
    """
        Контроллер для создания подписки.

        Attributes:
            model: Модель Subscription.
            template_name (str): Имя шаблона формы создания подписки.
            success_url (str): URL перенаправления после успешного создания подписки.
            form_class: Форма создания подписки.
    """

    model = Subscription
    template_name = 'subscriptions/subscription_form.html'
    success_url = reverse_lazy('blog:home')
    form_class = SubscriptionForm

    def form_valid(self, form):
        """
            Проверка валидности формы и создание подписки.
        """

        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        form.create_subscription(self.request.user, blog)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
            Получает данные контекста.
        """
        context = super().get_context_data(**kwargs)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        context['blog'] = blog
        return context


class SubscriptionListView(ListView):
    """
        Контроллер для списка подписок пользователя.

        Attributes:
            model: Модель Subscription.
            template_name (str): Имя шаблона списка подписок.
    """

    model = Subscription
    template_name = 'subscriptions/subscription_list.html'  # Создайте шаблон для списка подписок

    def get_queryset(self):
        """
            Получает список подписок пользователя.

            Returns:
                QuerySet: QuerySet с подписками.
        """
        user = self.request.user

        # Получаем ID блогов, на которые подписан текущий пользователь
        subscribed_blog_ids = Subscription.objects.filter(user=user, status=True).values_list('blog__id', flat=True)

        # Получаем опубликованные блоги, на которые подписан текущий пользователь
        subscribed_blogs = Blog.objects.filter(id__in=subscribed_blog_ids, published_on=True)

        # Получаем блоги, созданные текущим пользователем и опубликованные
        user_blogs = Blog.objects.filter(user=user, published_on=True)

        # Получаем блоги, созданные текущим пользователем, но неопубликованные
        user_unpublished_blogs = Blog.objects.filter(user=user, published_on=False)

        # Объединяем все полученные блоги и убираем возможные дубликаты
        combined_blogs = (user_blogs | subscribed_blogs | user_unpublished_blogs).distinct()

        return combined_blogs


class SubscriptionDeleteView(DeleteView):
    """
        Контроллер для удаления подписки.

        Attributes:
            model: Модель Subscription.
            template_name (str): Имя шаблона подтверждения удаления подписки.
            success_url (str): URL перенаправления после успешного удаления подписки.

    """
    model = Subscription
    template_name = 'subscriptions/subscription_confirm_delete.html'
    success_url = reverse_lazy('blog:home')

    def get_queryset(self):
        """
            Получает QuerySet подписок пользователя.

            Returns:
                QuerySet: QuerySet подписок пользователя.
        """
        return Subscription.objects.filter(user=self.request.user)

    def get_object(self, queryset=None):
        """
            Получает объект подписки.

            Args:
                queryset: QuerySet подписок.

            Returns:
                object: Объект подписки.
        """
        return get_object_or_404(self.get_queryset(), blog__slug=self.kwargs['slug'])
