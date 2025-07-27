from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .views import list_books, LibraryDetailView

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Function-based view URL pattern
    path('books/', views.list_books, name='list_books'),
    
    # Class-based view URL pattern
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),

    # Authentication URLs patterns using Django's built-in views
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register_view, name='register'),
]