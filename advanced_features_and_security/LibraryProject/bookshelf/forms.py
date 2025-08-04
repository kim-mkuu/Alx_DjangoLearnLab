"""
STEP 2 & 3: SECURE FORM IMPLEMENTATION
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

class BookForm(forms.ModelForm):
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
        Initialize form with additional security measures.
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
       Validate and sanitize author name.
        """
        author = self.cleaned_data.get('author', '').strip()