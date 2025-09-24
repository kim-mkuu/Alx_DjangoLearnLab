"""
Data models for the advanced_api_project application.

This module defines the core models for managing Authors and their Books.

Establishes a one-to-many relationship where an Author can have multiple Books. 
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class Author(models.Model):
    """
    Author model representing book authors in the system.

    The model stores basic information about authors and serves as parent in a one-to-many relationship with the Book model.
    """

    name = models.CharField(
        max_length=200,
        help_text="The full name of the author"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the author record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the author record was last updated"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        """Return a string representation of the author."""
        return self.name
    
    @property
    def books_count(self):
        """Return the number of books written by this author."""
        return self.books.count()
    
class Book(models.Model):
    """
    Book model representing books in the system.

    The models stores information about books and establishes a many-to-one relationship with the Author model.
    """

    title = models.CharField(
        max_length=300,
        help_text="The title of the book"
    )
    publication_year = models.IntegerField(
        validators=[
            MinValueValidator(1000, message="Publication year must be at least 1000"),
            MaxValueValidator(datetime.now().year,message="Publication year cannot be in the future")
        ],
        help_text="The year the book was published"
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        help_text="The author who wrote this book"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the book record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the book record was last updated"
    )
    class Meta:
        ordering = ['-publication_year', 'title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        unique_together = ['title', 'author']#ensures no duplicate books by the same author

    def __str__(self):
        """Return string representation of the book."""
        return f"{self.title} ({self.publication_year}) by {self.author.name}"
    
    @property
    def is_recent(self):
        """check if the book was published in the last 10 years."""
        current_year = datetime.now().year
        return self.publication_year >= (current_year -10)
        