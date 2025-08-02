from django.urls import path
from . import views

app_name = 'bookshelf'

urlpatterns = [
    # Book list view - requires can_view_all_books permission
    path('', views.book_list, name='book_list'),
    
    # Book detail view - requires can_view permission  
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    
    # Book creation - requires can_create permission
    path('create/', views.create_book, name='create_book'),
    
    # Book editing - requires can_edit permission
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'),
    
    # Book deletion - requires can_delete permission
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),
    
    # Bulk operations - requires can_bulk_operations permission
    path('bulk/', views.bulk_operations, name='bulk_operations'),
    
    # Search functionality - requires can_view_all_books permission
    path('search/', views.search_books, name='search_books'),
]