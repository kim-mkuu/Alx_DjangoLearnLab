from django.contrib import admin
from .models import Author, Book, Library, Librarian

# Author model admin configuration
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Author model.
    """
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Book model admin configuration
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Book model.
    """
    list_display = ('title', 'author')
    list_filter = ('author',)
    search_fields = ('title', 'author__name')
    ordering = ('title',)

# Library model admin configuration
@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Library model.
    """
    list_display = ('name', 'book_count')
    search_fields = ('name',)
    filter_horizontal = ('books',)  # Makes it easier to manage many-to-many relationships
    ordering = ('name',)
    
    def book_count(self, obj):
        """Display the number of books in each library"""
        return obj.books.count()
    book_count.short_description = 'Number of Books'

# Librarian model admin configuration
@admin.register(Librarian)
class LibrarianAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Librarian model.
    """
    list_display = ('name', 'library')
    list_filter = ('library',)
    search_fields = ('name', 'library__name')
    ordering = ('name',)