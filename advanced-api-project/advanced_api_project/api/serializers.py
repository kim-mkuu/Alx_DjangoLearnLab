"""
Custom serializers for the advanced API project.

This module defines serializers that handle complex data structures and nested relationships between Author and Book models, including custom validation logic and dynamic nested serialization.
"""

from rest_framework import serializers
from datetime import datetime
from .models import Author, Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the book model with custom validation.
    
    This serializer handles all Book models and implements custom validation to ensure, data integrity, particularly for the publication_year field which must not  be in the future.

    The serializer also provides additional compute fields and handles the relationship with the Author model appropriately.
    """
    #Compute Fields
    author_name = serializers.CharField(source='author.name', read_only=True)
    is_recent = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'publication_year',
            'author',
            'author_name', #Read-0nly compute field
            'is_recent', #Read-only compute field
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_publication_year(self, value):
        """
        Custom validation for publication_year field.
        
        Ensures that the publication year is not in the future and is within reasonable historical bounds for books.
        """

        current_year = datetime.now()

        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        if value < 1000:
            raise serializers.ValidationError(
                f"Publication year must be at least 1000."
            )
        return value
    
    def validate_title(self, value):
        """
        Custom validation for title field.

        Ensures the title is not empty after stripping whitespace and meets minimum length requirements.
        """

        cleaned_title = value.strip()

        if not cleaned_title:
            raise serializers.ValidationError(
                "Title can not be empty or contain only whitespace."
            )
        
        if len(cleaned_title) < 2:
            raise serializers.ValidationError(
                "Title must be at least 2 characters long."
            )
        
        return cleaned_title
    
    def validate(self, data):
        """
        Object-level validation for the entire book instance.

        Performs cross-field validation and business logic checks that involve multiple fields or external constraints.
        """
        #checks for duplicate books by the same author(if creating new)
        if not self.instance: #Only for creation, not updates
            title = data.get('title', '').strip()
            author = data.get('author')

            if author and Book.objects.filter(title__iexact=title, author=author).exists():
                raise serializers.ValidationError(
                    f"A book with the tittle '{title}' by {author.name} already exists."
                )
            
        return data
    
class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model with nested Book serialization.

    This serializer demonstrates advanced DRF techniques including:
    -Dynamic nested serialization of related books
    -Custom fields for computed values
    -Flexible serialization based on context
    -Efficient querying with prefetch_related optimization

    The serializer can operate in different modes based the context:
    -'list' context: Minimal book information for performance
    -'detail' context: Full nested book serialization
    """

    #Nested serialization of related books
    books = BookSerializer(many=True, read_only=True)

    #Computed fields
    books_count = serializers.IntegerField(read_only=True)
    recent_books_count = serializers.SerializerMethodField()
    latest_publication_year = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id',
            'name',
            'books_count',
            'recent_books_count',
            'latest_publication_year',
            'books', #Nested books
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_recent_books_count(self, obj):
        """
        Calculate the number of recent books (published in last 10 years)
        """
        current_year = datetime.now().year
        return obj.books.filter(publication_year__gte=current_year - 10).count()
    
    def get_latest_publication_year(self, obj):
        """
        Get the publication of the author's most recent book."""
        latest_book = obj.books.order_by('-publication_year').first()
        return latest_book.publication_year if latest_book else None
    def validate_name(self, value):
        """
        Custom validation for author name field.
        
        Ensures the name meets quality standards and is properly formatted.
        """
        cleaned_name = value.strip()

        if not cleaned_name:
            raise serializers.ValidationError(
                "Author name can not be empty or contain only whitespace."
            )
        
        if len(cleaned_name) < 2:
            raise serializers.ValidationError(
                "Author name must be at least 2 characters long."  
            )
        
        #check for duplicate names (case-insensitive)
        if not self.instance: #Only for creation
            if Author.objects.filter(name__iexact=cleaned_name).exists():
                raise serializers.ValidationError(
                    f"An author with the name '{cleaned_name}' already exists."
                )
        return cleaned_name
    
    def to_representation(self, instance):
        """
        Customize the serialized representation based on context.
        
        This method allows for dynamic serialization behavior:
        -In list views, we might want minimal book information
        -In detail views, we want full nested serialization
        """

        data = super().to_representation(instance)

        #Customize based on context
        request = self.context.get('request')
        if request and request.query_params.get('minimal') == 'true':
            #Return minimal representation without nested books
            data.pop('books', None)

        return data
    
class AuthorDetailSerializer(AuthorSerializer):
    """
    Detailed serializer for Author with enhanced book information.
    
    This serializer extends the base AuthorSerializer to provide more detailed information suitable for detail views, including additional computed fields and enhanced nested serialization.
    """

    #Override books field with more detailed serialization
    books = BookSerializer(many=True, read_only=True)

    #Additional detail fields
    first_publication_year = serializers.SerializerMethodField()
    publication_span = serializers.SerializerMethodField()

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + [
            'first_publication_year',
            'publication_span'
        ]
    
    def get_first_publication_year(self, obj):
        """Get the publication year of the author's first book."""
        first_book = obj.books.order_by('publication_year').first()
        return first_book.publication_year if first_book else None
    
    def get_publication_span(self, obj):
        """Calculate the span of years between first and latest publications."""
        first_year = self.get_first_publication_year(obj)
        latest_year = self.get_latest_publication_year(obj)

        if first_year and latest_year and first_year != latest_year:
            return latest_year - first_year
        return 0
    
#Alternative simplified serializers for different use cases
class BookMinimalSerializer(serializers.ModelSerializer):
    """Minimal Book serializer for list views and nested representations."""

    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year']

class AuthorMinimalSerializer(serializers.ModelSerializer):
    """Minimal Author serializer for list views and references."""

    books_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'books_count']         