from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Book, CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the CustomUser model.
    Extends Django's default UserAdmin to handle additional fields.
    """

    # Fields to display in the user list view
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'date_of_birth',
        'age_display',
        'profile_photo_display',
        'is_staff', 
        'is_active',
        'date_joined'
    )
    
    # Fields that can be searched
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # Fields that can be filtered in the right sidebar
    list_filter = (
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'date_joined',
        'date_of_birth'
    )
    
    # Ordering of the user list
    ordering = ('username',)
    
    # Fieldsets for the user detail/edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('date_of_birth', 'profile_photo'),
            'classes': ('collapse',),  # Makes this section collapsible
        }),
    )
    
    # Fields to include when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('date_of_birth', 'profile_photo'),
            'classes': ('collapse',),
        }),
    )
    
    def age_display(self, obj):
        """Display calculated age in the admin list view"""
        age = obj.age
        if age is not None:
            return f"{age} years"
        return "Not specified"
    age_display.short_description = 'Age'
    
    def profile_photo_display(self, obj):
        """Display profile photo thumbnail in the admin list view"""
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_photo.url
            )
        return "No photo"
    profile_photo_display.short_description = 'Profile Photo'

# Register the CustomUser model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)

#Book admin configuration
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Book model.
    """
    list_display = ('title', 'author', 'publication_year')
    list_filter = ('author', 'publication_year',)
    search_fields = ('title', 'author')
    ordering = ('publication_year',)

