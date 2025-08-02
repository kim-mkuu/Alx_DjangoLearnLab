from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
   
    # Book views with permission protection
    path('books/', views.list_books, name='list_books'),  # Requires can_view_all_books
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),  # Requires can_view
    
    # Class-based view URL pattern
    path('library/<int:pk>/', views.LibraryDetailView.as_view(), name='library_detail'),
    
    # Authentication URL patterns using Django's built-in views
    path('login/', LoginView.as_view(template_name='relationship_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='relationship_app/logout.html'), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Role-based URL patterns with enhanced permission checks
    path('admin/', views.admin_view, name='admin_view'),  # Requires Admin role + can_view_library_stats
    path('librarian/', views.librarian_view, name='librarian_view'),  # Requires Librarian role + can_manage_library
    path('member/', views.member_view, name='member_view'),  # Requires Member role + can_view

    # Permission-protected Book CRUD operations
    path('add_book/', views.add_book, name='add_book'),  # Requires can_create

]