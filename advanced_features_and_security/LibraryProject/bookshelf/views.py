"""
SECURE DATA ACCESS 
This module implements secure view functions with proper input validation,
CSRF protection, and SQL injection prevention measures.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.html import escape
from django.core.validators import validate_integer
import logging

from .models import Book
from .forms import BookForm

# Configure logging for security events
logger = logging.getLogger('django.security')

# SECURE HELPER FUNCTIONS
def validate_book_id(book_id):
    """
    SECURITY: Validate book ID to prevent injection attacks
    Returns validated integer or raises ValidationError
    """
    try:
        validate_integer(book_id)
        return int(book_id)
    except (ValueError, ValidationError):
        logger.warning(f"Invalid book ID attempted: {book_id}")
        raise ValidationError("Invalid book ID format")

def sanitize_search_query(query):
    """
    SECURITY: Sanitize search input to prevent XSS and injection attacks
    """
    if not query:
        return ""
    
    # Escape HTML to prevent XSS
    sanitized = escape(query.strip())
    
    # Limit query length to prevent DoS
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized

# SECURE BOOK LIST VIEW
@permission_required('bookshelf.can_view_all_books', raise_exception=True)
@csrf_protect  # Explicit CSRF protection
def book_list(request):
    """
    SECURE: Function-based view that displays a list of all books from bookshelf app.
    Implements proper permission checking and secure data access.
    """
    try:
        # Use Django ORM to prevent SQL injection
        books = Book.objects.select_related().order_by('title')
        
        # Add permission context safely
        context = {
            'books': books,
            'title': 'All Books - Bookshelf',
            'can_create': request.user.has_perm('bookshelf.can_create'),
            'can_edit': request.user.has_perm('bookshelf.can_edit'),
            'can_delete': request.user.has_perm('bookshelf.can_delete'),
        }
        
        logger.info(f"Book list accessed by user: {request.user.username}")
        return render(request, 'bookshelf/book_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in book_list view: {str(e)}")
        messages.error(request, "An error occurred while loading books.")
        return render(request, 'bookshelf/book_list.html', {'books': []})

# SECURE BOOK DETAIL VIEW
@permission_required('bookshelf.can_view', raise_exception=True)
@csrf_protect
def book_detail_view(request, book_id):
    """
    SECURE: View to display individual book details with input validation.
    """
    try:
        # Validate book_id to prevent injection
        validated_id = validate_book_id(book_id)
        
        # Use Django ORM get_object_or_404 to prevent SQL injection
        book = get_object_or_404(Book, id=validated_id)
        
        context = {
            'book': book,
            'can_edit': request.user.has_perm('bookshelf.can_edit'),
            'can_delete': request.user.has_perm('bookshelf.can_delete'),
        }
        
        logger.info(f"Book detail viewed: {book.title} by user: {request.user.username}")
        return render(request, 'bookshelf/book_detail.html', context)
        
    except ValidationError:
        messages.error(request, "Invalid book identifier.")
        return redirect('bookshelf:book_list')
    except Exception as e:
        logger.error(f"Error in book_detail_view: {str(e)}")
        messages.error(request, "Book not found.")
        return redirect('bookshelf:book_list')

# SECURE BOOK CREATION
@permission_required('bookshelf.can_create', raise_exception=True)
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])  # Restrict HTTP methods
def create_book(request):
    """
    SECURE: View to create a new book with comprehensive input validation.
    """
    if request.method == 'POST':
        try:
            # Use Django forms for input validation and CSRF protection
            form = BookForm(request.POST)
            
            if form.is_valid():
                # Use form.save() to prevent SQL injection
                book = form.save()
                
                logger.info(f"Book created: {book.title} by user: {request.user.username}")
                messages.success(request, f'Book "{book.title}" has been created successfully!')
                return redirect('bookshelf:book_list')
            else:
                # Log form validation failures
                logger.warning(f"Invalid book creation attempt by user: {request.user.username}")
                messages.error(request, 'Please correct the errors below.')
                
        except Exception as e:
            logger.error(f"Error creating book: {str(e)}")
            messages.error(request, 'An error occurred while creating the book.')
    else:
        form = BookForm()
    
    context = {
        'form': form,
        'title': 'Create New Book',
        'books': Book.objects.all()[:5],  # Show recent books for reference
    }
    return render(request, 'bookshelf/create_book.html', context)

# SECURE BOOK EDITING
@permission_required('bookshelf.can_edit', raise_exception=True)
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def edit_book(request, book_id):
    """
    SECURE: View to edit an existing book with input validation.
    """
    try:
        # Validate and get book safely
        validated_id = validate_book_id(book_id)
        book = get_object_or_404(Book, id=validated_id)
        
        if request.method == 'POST':
            # Use Django forms for validation
            form = BookForm(request.POST, instance=book)
            
            if form.is_valid():
                updated_book = form.save()
                
                logger.info(f"Book updated: {updated_book.title} by user: {request.user.username}")
                messages.success(request, f'Book "{updated_book.title}" has been updated successfully!')
                return redirect('bookshelf:book_list')
            else:
                logger.warning(f"Invalid book update attempt for book ID: {book_id}")
                messages.error(request, 'Please correct the errors below.')
        else:
            form = BookForm(instance=book)
        
        context = {
            'form': form,
            'book': book,
            'title': f'Edit Book: {book.title}',
            'books': Book.objects.exclude(id=validated_id)[:5],
        }
        return render(request, 'bookshelf/edit_book.html', context)
        
    except ValidationError:
        messages.error(request, "Invalid book identifier.")
        return redirect('bookshelf:book_list')
    except Exception as e:
        logger.error(f"Error editing book: {str(e)}")
        messages.error(request, "Book not found.")
        return redirect('bookshelf:book_list')

# SECURE BOOK DELETION
@permission_required('bookshelf.can_delete', raise_exception=True)
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def delete_book(request, book_id):
    """
    SECURE: View to delete a book with proper validation and logging.
    """
    try:
        validated_id = validate_book_id(book_id)
        book = get_object_or_404(Book, id=validated_id)
        
        if request.method == 'POST':
            book_title = book.title
            book.delete()
            
            logger.warning(f"Book deleted: {book_title} by user: {request.user.username}")
            messages.success(request, f'Book "{book_title}" has been deleted successfully!')
            return redirect('bookshelf:book_list')
        
        context = {
            'book': book,
            'title': f'Delete Book: {book.title}',
            'books': Book.objects.exclude(id=validated_id),
        }
        return render(request, 'bookshelf/confirm_delete.html', context)
        
    except ValidationError:
        messages.error(request, "Invalid book identifier.")
        return redirect('bookshelf:book_list')
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        messages.error(request, "Book not found.")
        return redirect('bookshelf:book_list')

# SECURE BULK OPERATIONS
@permission_required('bookshelf.can_bulk_operations', raise_exception=True)
@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def bulk_operations(request):
    """
    SECURE: View for bulk operations with comprehensive input validation.
    """
    books = Book.objects.all()
    
    if request.method == 'POST':
        try:
            # Validate selected book IDs
            selected_books = request.POST.getlist('selected_books')
            action = request.POST.get('action', '').strip()
            
            # Validate book IDs
            validated_ids = []
            for book_id in selected_books:
                try:
                    validated_ids.append(validate_book_id(book_id))
                except ValidationError:
                    logger.warning(f"Invalid book ID in bulk operation: {book_id}")
                    continue
            
            if not validated_ids:
                messages.error(request, "No valid books selected.")
                return redirect('bookshelf:book_list')
            
            # Validate action
            allowed_actions = ['delete', 'update_year']
            if action not in allowed_actions:
                logger.warning(f"Invalid bulk action attempted: {action}")
                messages.error(request, "Invalid action selected.")
                return redirect('bookshelf:book_list')
            
            # Perform secure bulk operations
            if action == 'delete':
                deleted_count = Book.objects.filter(id__in=validated_ids).count()
                Book.objects.filter(id__in=validated_ids).delete()
                
                logger.warning(f"Bulk delete: {deleted_count} books by user: {request.user.username}")
                messages.success(request, f'Successfully deleted {deleted_count} books.')
                
            elif action == 'update_year':
                new_year = request.POST.get('new_year', '').strip()
                try:
                    validate_integer(new_year)
                    year_int = int(new_year)
                    
                    # Validate year range
                    if not (1000 <= year_int <= 2030):
                        raise ValidationError("Year must be between 1000 and 2030")
                    
                    updated_count = Book.objects.filter(id__in=validated_ids).update(
                        publication_year=year_int
                    )
                    
                    logger.info(f"Bulk year update: {updated_count} books to {year_int}")
                    messages.success(request, f'Successfully updated {updated_count} books.')
                    
                except (ValueError, ValidationError):
                    logger.warning(f"Invalid year in bulk update: {new_year}")
                    messages.error(request, 'Please enter a valid year between 1000 and 2030.')
            
            return redirect('bookshelf:book_list')
            
        except Exception as e:
            logger.error(f"Error in bulk operations: {str(e)}")
            messages.error(request, "An error occurred during bulk operation.")
    
    context = {
        'books': books,
        'title': 'Bulk Operations - Bookshelf',
    }
    return render(request, 'bookshelf/bulk_operations.html', context)

# SECURE SEARCH FUNCTIONALITY
@permission_required('bookshelf.can_view_all_books', raise_exception=True)
@csrf_protect
def search_books(request):
    """
    SECURE: Search functionality with input sanitization and SQL injection prevention.
    """
    try:
        # Sanitize search query
        raw_query = request.GET.get('q', '')
        query = sanitize_search_query(raw_query)
        
        books = Book.objects.all()
        
        if query:
            # Use Django ORM Q objects to prevent SQL injection
            books = books.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            ).distinct()
            
            logger.info(f"Search performed: '{query}' by user: {request.user.username}")
        
        context = {
            'books': books,
            'query': query,
            'title': f'Search Results for "{query}"' if query else 'Search Books',
        }
        return render(request, 'bookshelf/search_results.html', context)
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        messages.error(request, "An error occurred during search.")
        return render(request, 'bookshelf/search_results.html', {'books': [], 'query': ''})

# SECURE API ENDPOINT
@permission_required('bookshelf.can_view_all_books', raise_exception=True)
@csrf_protect
@require_http_methods(["GET"])
def api_books(request):
    """
    SECURE: API endpoint with proper validation and error handling.
    """
    try:
        books = Book.objects.all()
        
        # Sanitize output data
        books_data = []
        for book in books:
            books_data.append({
                'id': book.id,
                'title': escape(book.title),
                'author': escape(book.author),
                'publication_year': book.publication_year,
            })
        
        return JsonResponse({
            'status': 'success',
            'data': books_data,
            'count': len(books_data)
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while fetching books.'
        }, status=500)