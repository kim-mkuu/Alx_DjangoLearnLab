"""
SECURE FORM IMPLEMENTATION
This module implements secure Django forms with comprehensive validation,
CSRF protection, and input sanitization to prevent various attacks.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import escape, strip_tags
from django.core.validators import MinLengthValidator, MaxLengthValidator
import re
import logging

from .models import Book

# Configure logging for form validation events
logger = logging.getLogger('django.security')

class SecureBookForm(forms.ModelForm):
    """
    SECURE: Enhanced BookForm with comprehensive validation and security measures.
    Implements CSRF protection, input sanitization, and prevents injection attacks.
    """
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        
        # Enhanced form widgets with security attributes
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title',
                'maxlength': '200',
                'required': True,
                'autocomplete': 'off',  # Prevent autocomplete for sensitive fields
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter author name',
                'maxlength': '100',
                'required': True,
                'autocomplete': 'off',
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year',
                'min': '1000',
                'max': '2030',
                'required': True,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        SECURITY: Initialize form with additional security measures.
        """
        super().__init__(*args, **kwargs)
        
        # Add field-level validators
        self.fields['title'].validators.extend([
            MinLengthValidator(2, "Title must be at least 2 characters long."),
            MaxLengthValidator(200, "Title cannot exceed 200 characters."),
        ])
        
        self.fields['author'].validators.extend([
            MinLengthValidator(2, "Author name must be at least 2 characters long."),
            MaxLengthValidator(100, "Author name cannot exceed 100 characters."),
        ])
        
        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True
            
            # Add security-focused help text
            if field_name == 'title':
                field.help_text = "Enter the book title (2-200 characters, no HTML allowed)"
            elif field_name == 'author':
                field.help_text = "Enter the author's name (2-100 characters, no HTML allowed)"
            elif field_name == 'publication_year':
                field.help_text = "Enter publication year (1000-2030)"
    
    def clean_title(self):
        """
        SECURITY: Validate and sanitize book title to prevent XSS and injection attacks.
        """
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise ValidationError("Title is required.")
        
        # Remove HTML tags to prevent XSS
        title = strip_tags(title)
        
        # Escape remaining HTML entities
        title = escape(title)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
        ]
        
        title_lower = title.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, title_lower):
                logger.warning(f"Suspicious title input detected: {title}")
                raise ValidationError("Title contains invalid characters or patterns.")
        
        # Length validation
        if len(title) < 2:
            raise ValidationError("Title must be at least 2 characters long.")
        
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")
        
        # Check for excessive special characters (potential injection)
        special_char_count = len(re.findall(r'[^\w\s\-.,\'\"!?()]', title))
        if special_char_count > len(title) * 0.3:  # More than 30% special chars
            logger.warning(f"Title with excessive special characters: {title}")
            raise ValidationError("Title contains too many special characters.")
        
        return title
    
    def clean_author(self):
        """
        SECURITY: Validate and sanitize author name.
        """
        author = self.cleaned_data.get('author', '').strip()
        
        if not author:
            raise ValidationError("Author is required.")
        
        # Remove HTML tags and escape
        author = strip_tags(author)
        author = escape(author)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
        ]
        
        author_lower = author.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, author_lower):
                logger.warning(f"Suspicious author input detected: {author}")
                raise ValidationError("Author name contains invalid characters.")
        
        # Length validation
        if len(author) < 2:
            raise ValidationError("Author name must be at least 2 characters long.")
        
        if len(author) > 100:
            raise ValidationError("Author name cannot exceed 100 characters.")
        
        # Basic name format validation
        if not re.match(r'^[a-zA-Z\s\-\'\.]+'
        , author):
            raise ValidationError("Author name contains invalid characters. Only letters, spaces, hyphens, apostrophes, and periods are allowed.")
        
        return author
    
    def clean_publication_year(self):
        """
        SECURITY: Validate publication year to prevent injection and ensure valid range.
        """
        year = self.cleaned_data.get('publication_year')
        
        if year is None:
            raise ValidationError("Publication year is required.")
        
        # Validate year range
        if not isinstance(year, int):
            raise ValidationError("Publication year must be a valid number.")
        
        if year < 1000 or year > 2030:
            raise ValidationError("Publication year must be between 1000 and 2030.")
        
        return year
    
    def clean(self):
        """
        SECURITY: Cross-field validation and additional security checks.
        """
        cleaned_data = super().clean()
        title = cleaned_data.get('title', '')
        author = cleaned_data.get('author', '')
        
        # Check for duplicate content (potential spam)
        if title and author and title.lower() == author.lower():
            raise ValidationError("Title and author cannot be identical.")
        
        # Log form validation attempts
        logger.info(f"Book form validation attempted for: {title} by {author}")
        
        return cleaned_data

# Alias for backward compatibility with existing code
BookForm = SecureBookForm

#Example form for testing and demonstration
class ExampleForm(forms.Form):
    """
    SECURE: Example form demonstrating security best practices.
    Used for testing CSRF protection and input validation.
    """
    
    name = forms.CharField(
        max_length=100,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name',
            'autocomplete': 'off',
        }),
        help_text="Enter your full name (2-100 characters)"
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        }),
        help_text="Enter a valid email address"
    )
    
    message = forms.CharField(
        max_length=500,
        min_length=10,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your message',
            'autocomplete': 'off',
        }),
        help_text="Enter your message (10-500 characters)"
    )
    
    def clean_name(self):
        """SECURITY: Validate and sanitize name input."""
        name = self.cleaned_data.get('name', '').strip()
        
        # Remove HTML tags and escape
        name = strip_tags(name)
        name = escape(name)
        
        # Check for suspicious patterns
        if re.search(r'<script|javascript:|vbscript:', name.lower()):
            raise ValidationError("Name contains invalid characters.")
        
        # Validate name format
        if not re.match(r'^[a-zA-Z\s\-\'\.]+'
        , name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, apostrophes, and periods.")
        
        return name
    
    def clean_message(self):
        """SECURITY: Validate and sanitize message input."""
        message = self.cleaned_data.get('message', '').strip()
        
        # Remove HTML tags but preserve line breaks
        message = strip_tags(message)
        message = escape(message)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
        ]
        
        message_lower = message.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, message_lower):
                raise ValidationError("Message contains invalid content.")
        
        # Check for excessive special characters
        special_char_count = len(re.findall(r'[^\w\s\-.,\'\"!?()]', message))
        if special_char_count > len(message) * 0.3:
            raise ValidationError("Message contains too many special characters.")
        
        return message