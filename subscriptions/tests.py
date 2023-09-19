import json
from django.urls import reverse
from blog.models import Blog
from subscriptions.forms import SubscriptionForm
from subscriptions.models import Subscription
from users.tests import SetupTestCase


class SubscriptionModelTest(SetupTestCase):
    def setUp(self):
        super().setUp()

    def test_create_subscription(self):
        blog = Blog.objects.create(title='Test blog')
        sub = Subscription.objects.create(
            user=self.user,
            blog=blog,
            status=True
        )
        self.assertEqual(sub.user, self.user)
        self.assertEqual(sub.blog, blog)


class SubscriptionViewTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test')
        self.sub = Subscription.objects.create(
            user=self.user,
            blog=self.blog
        )

    def test_create_view(self):
        self.client.login(phone='123456789', password='testpass123')
        url = reverse('subscriptions:subscription_create', args=[self.blog.slug])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:home'))

    def test_delete_view(self):
        self.client.login(phone='123456789', password='testpass123')
        url = reverse('subscriptions:subscription_delete', args=[self.sub.blog.slug])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)


class SubscriptionFormTest(SetupTestCase):

    def test_valid_form(self):
        self.blog = Blog.objects.create(title='Test')
        form = SubscriptionForm(data={'user': self.user,
                                      'blog': self.blog,
                                      'status': True,
                                      'payment_status': True
                                      }
                                )
        self.assertTrue(form.is_valid())


class SubscriptionListViewTest(SetupTestCase):

    def test_subscription_list_view_authenticated_user(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.get(reverse('subscriptions:subscription_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/subscription_list.html')

    def test_subscription_list_view_unauthenticated_user(self):
        response = self.client.get(reverse('subscriptions:subscription_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'subscriptions/subscription_list.html', html=True)


class StripeIntentViewTest(SetupTestCase):
    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test Blog', price=10)
        self.url = reverse('subscriptions:create-payment-intent', kwargs={'pk': self.blog.pk})

    def test_stripe_intent_view(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.post(
            self.url,
            json.dumps({'phone': '123456789', 'blog_slug': self.blog.slug}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)


class CreateCheckoutSessionViewTest(SetupTestCase):
    def test_create_checkout_session_view(self):

        self.client.login(phone='123456789', password='testpass123')

        blog = Blog.objects.create(title='Test Blog', price=10)
        url = reverse('subscriptions:create-checkout-session', kwargs={'slug': blog.slug})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)


class SuccessViewTest(SetupTestCase):
    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test Blog', price=10)
        self.url = reverse('subscriptions:success', kwargs={'slug': self.blog.slug})

    def test_success_view(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subscriptions/success.html')

        subscription = Subscription.objects.get(user=self.user, blog=self.blog)
        self.assertTrue(subscription.status)
        self.assertTrue(subscription.payment_status)
