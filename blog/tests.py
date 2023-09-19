from django.urls import reverse
from blog.forms import BlogForm
from blog.models import Blog, Comment
from users.tests import SetupTestCase


class BlogViewTests(SetupTestCase):

    def setUp(self):
        super().setUp()

        self.client.login(phone='123456789', password='testpass123')


class BlogModelTest(SetupTestCase):

    def test_blog_creation(self):
        blog = Blog.objects.create(
            title='Test Blog',
            description='Test Description',
        )
        self.assertEqual(blog.title, 'Test Blog')
        self.assertEqual(blog.description, 'Test Description')

    def test_slug_creation(self):
        blog = Blog.objects.create(title='Test Blog')
        self.assertEqual(blog.slug, 'test-blog')


class BlogListViewTest(SetupTestCase):

    def test_blog_list_view(self):
        Blog.objects.create(title='Blog 1', description='Description 1', published_on=True)
        Blog.objects.create(title='Blog 2', description='Description 2', published_on=True)

        url = reverse('blog:blog_list')
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_list.html')


class BlogDetailViewTest(SetupTestCase):

    def test_blog_detail_view(self):
        blog = Blog.objects.create(title='Test')
        url = reverse('blog:blog_detail', args=[blog.slug])
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/blog_detail.html')


class BlogFormTest(SetupTestCase):

    def test_valid_data(self):
        form = BlogForm(data={
            'title': 'Test',
            'description': 'Test',
            'price': 10,
            'is_paid': True,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = BlogForm(data={})
        self.assertFalse(form.is_valid())


class CommentCreationTest(SetupTestCase):
    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test Blog', description='Test Description')
        self.url = reverse('blog:blog_detail', args=[self.blog.slug])

    def test_comment_creation_authenticated_user(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.post(self.url, {'comment': 'Test Comment'})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.comment, 'Test Comment')

    def test_comment_creation_unauthenticated_user(self):
        response = self.client.post(self.url, {'comment': 'Test Comment'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 0)


class BlogUpdateViewTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test Blog', description='Test Description')
        self.url = reverse('blog:blog_update', args=[self.blog.slug])

    def test_blog_update_view_authenticated_user(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'price': 10,
            'is_paid': True,
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

        updated_blog = Blog.objects.get(pk=self.blog.pk)
        self.assertEqual(updated_blog.title, 'Updated Title')
        self.assertEqual(updated_blog.description, 'Updated Description')

    def test_blog_update_view_unauthenticated_user(self):
        response = self.client.post(self.url, {'title': 'Updated Title', 'description': 'Updated Description'})
        self.assertEqual(response.status_code, 302)

        updated_blog = Blog.objects.get(pk=self.blog.pk)
        self.assertEqual(updated_blog.title, 'Test Blog')
        self.assertEqual(updated_blog.description, 'Test Description')


class BlogDeleteViewTest(SetupTestCase):

    def setUp(self):
        super().setUp()
        self.blog = Blog.objects.create(title='Test Blog', description='Test Description')
        self.url = reverse('blog:blog_delete', args=[self.blog.slug])

    def test_blog_delete_view_authenticated_user(self):
        self.client.login(phone='123456789', password='testpass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Blog.objects.filter(pk=self.blog.pk).exists())

    def test_blog_delete_view_unauthenticated_user(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Blog.objects.filter(pk=self.blog.pk).exists())
