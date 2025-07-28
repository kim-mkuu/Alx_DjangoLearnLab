from django.contrib import admin
from .models import Author, Book, Library, Librarian, UserProfile

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
    list_display = ('title', 'author', 'publication_year')
    list_filter = ('author', 'publication_year')
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

# UserProfile model admin configuration
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for managing UserProfile model and user roles.
    """
    list_display = ('user', 'role', 'user_email', 'date_joined')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('user__username',)
    
    def user_email(self, obj):
        """Display user's email address"""
        return obj.user.email
    user_email.short_description = 'Email'
    
    def date_joined(self, obj):
        """Display when user joined"""
        return obj.user.date_joined.strftime("%Y-%m-%d")
    date_joined.short_description = 'Date Joined'