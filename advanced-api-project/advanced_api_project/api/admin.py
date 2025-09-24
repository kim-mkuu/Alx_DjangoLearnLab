"""
Django admin configuration for the API models.

This model customizes the Django admin interface for better management of Author and Book model, providing enhanced filtering and display options.
"""

from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Author model.
    
    Provides enhanced admin interface with search, filtering and custom display fields for a better author management.
    """

    list_display = ['name', 'books_count', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'books_count']
    ordering = ['name']

    def books_count(self, obj):
        """Display the number of books for each author."""
        return obj.books.count()
    books_count.short_description = 'Number of Books'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin configuration of the Book model.
    
    Provides enhanced admin interface with search, filtering, and custom display fields for better book management.
    """

    list_display = ['title', 'author', 'publication_year', 'is_recent', 'created_at']
    search_fields = ['title', 'author_name']
    list_filter = ['publication_year', 'author', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-publication_year', 'title']
    autocomplete_fields = ['author']

    def is_recent(self, obj):
        """ Display if the book us recent(published in the last 10 years)"""
        return obj.is_recent
    is_recent.boolean = True
    is_recent.short_description = 'Recent Publication'