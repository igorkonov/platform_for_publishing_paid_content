import os
import django
from django.test import TestCase
from django.urls import reverse
from users.forms import CustomPasswordResetForm
from users.models import User

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

django.setup()


class SetupTestCase(TestCase):

    def setUp(self):
        self.user = User(
            phone='123456789',
            avatar='avatar.jpg',
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        self.user.set_password('testpass123')
        self.user.save()


class UserModelTest(SetupTestCase):

    def test_user_created(self):
        user = User.objects.get(phone='123456789')
        self.assertEqual(user.phone, '123456789')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_check_password(self):
        user = User.objects.get(phone='123456789')
        self.assertTrue(user.check_password('testpass123'))


class LoginViewTest(SetupTestCase):

    def test_login_page(self):
        url = reverse('users:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login(self):
        url = reverse('users:login')
        data = {
            'username': '123456789',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('blog:home'))


class ProfileUpdateViewTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('users:profile')
        self.client.login(username='123456789', password='testpass123')

    def test_profile_update_view_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_profile_update_view_updates_profile(self):
        data = {
            'phone': '123456789',
            'avatar': 'avatar.jpg',
        }
        self.client.post(self.url, data)
        self.assertEqual(self.user.phone, '123456789')
        self.assertEqual(self.user.avatar, 'avatar.jpg')

    def test_profile_update_view_redirects_to_blog_home(self):
        data = {
            'phone': '123456789',
            'avatar': 'avatar.jpg',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('blog:home'))


class CustomPasswordResetFormTest(SetupTestCase):

    def test_valid_form(self):
        form_data = {
            'phone': '123456789',
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form_data = {
            'phone': 'invalidphone',
        }
        form = CustomPasswordResetForm(data=form_data)
        self.assertFalse(form.is_valid())


class CustomPasswordResetViewTest(SetupTestCase):

    def test_password_reset_view(self):
        url = reverse('users:password_reset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset_form.html')

    def test_password_reset_email_sent(self):
        url = reverse('users:password_reset')
        data = {
            'phone': '123456789',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_password_reset_confirm_view(self):

        uid = 'uid'
        token = 'token'
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_complete_view(self):
        url = reverse('users:password_reset_complete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
