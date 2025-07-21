from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Book

# Tests for the Book model and admin interface
class AdminTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin',
            password='testpassword'
        )
        self.client = Client()
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            publication_year=2023
        )
    
    def test_book_admin_list(self):
        self.client.login(username='admin', password='testpassword')
        response = self.client.get('/admin/bookshelf/book/')
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Test Author')
        self.assertContains(response, '2023')
    
    def test_admin_search(self):
        self.client.login(username='admin', password='testpassword')
        response = self.client.get('/admin/bookshelf/book/?q=Test')
        self.assertContains(response, 'Test Book')