# bookshelf/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Book

# Step 3: Enforce Permissions in Views - Bookshelf App Views

@permission_required('bookshelf.can_view_all_books', raise_exception=True)
def book_list(request):
    """
    Function-based view that displays a list of all books from bookshelf app.
    Requires 'can_view_all_books' permission to access.
    Step 3: Permission enforcement using @permission_required decorator with raise_exception=True
    """
    books = Book.objects.all().order_by('title')
    context = {
        'books': books,
        'title': 'All Books - Bookshelf',
        'can_create': request.user.has_perm('bookshelf.can_create'),
        'can_edit': request.user.has_perm('bookshelf.can_edit'),
        'can_delete': request.user.has_perm('bookshelf.can_delete'),
    }
    return render(request, 'bookshelf/book_list.html', context)

@permission_required('bookshelf.can_view', raise_exception=True)
def book_detail_view(request, book_id):
    """
    View to display individual book details from bookshelf app.
    Requires 'can_view' permission with raise_exception=True for proper error handling.
    """
    book = get_object_or_404(Book, id=book_id)
    context = {
        'book': book,
        'can_edit': request.user.has_perm('bookshelf.can_edit'),
        'can_delete': request.user.has_perm('bookshelf.can_delete'),
    }
    return render(request, 'bookshelf/book_detail.html', context)

@permission_required('bookshelf.can_create', raise_exception=True)
@login_required
def create_book(request):
    """
    View to create a new book in bookshelf app.
    Requires 'can_create' permission - typically assigned to Editors and Admins groups.
    Uses raise_exception=True to show 403 Forbidden for unauthorized users.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        publication_year = request.POST.get('publication_year')
        
        if title and author and publication_year:
            try:
                book = Book.objects.create(
                    title=title,
                    author=author,
                    publication_year=int(publication_year)
                )
                messages.success(request, f'Book "{book.title}" has been created successfully!')
                return redirect('bookshelf:book_list')
            except ValueError:
                messages.error(request, 'Please enter a valid publication year.')
        else:
            messages.error(request, 'All fields are required.')
    
    context = {
        'title': 'Create New Book',
        'books': Book.objects.all()[:5],  # Show recent books for reference
    }
    return render(request, 'bookshelf/create_book.html', context)

@permission_required('bookshelf.can_edit', raise_exception=True)
@login_required
def edit_book(request, book_id):
    """
    View to edit an existing book in bookshelf app.
    Requires 'can_edit' permission - typically assigned to Editors and Admins groups.
    Uses raise_exception=True for consistent permission error handling.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        publication_year = request.POST.get('publication_year')
        
        if title and author and publication_year:
            try:
                book.title = title
                book.author = author
                book.publication_year = int(publication_year)
                book.save()
                messages.success(request, f'Book "{book.title}" has been updated successfully!')
                return redirect('bookshelf:book_list')
            except ValueError:
                messages.error(request, 'Please enter a valid publication year.')
        else:
            messages.error(request, 'All fields are required.')
    
    context = {
        'book': book,
        'title': f'Edit Book: {book.title}',
        'books': Book.objects.exclude(id=book_id)[:5],  # Show other books
    }
    return render(request, 'bookshelf/edit_book.html', context)

@permission_required('bookshelf.can_delete', raise_exception=True)
@login_required
def delete_book(request, book_id):
    """
    View to delete a book from bookshelf app.
    Requires 'can_delete' permission - typically assigned to Admins group only.
    Uses raise_exception=True to ensure proper 403 handling for unauthorized access.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" has been deleted successfully!')
        return redirect('bookshelf:book_list')
    
    context = {
        'book': book,
        'title': f'Delete Book: {book.title}',
        'books': Book.objects.exclude(id=book_id),  # Show remaining books
    }
    return render(request, 'bookshelf/confirm_delete.html', context)

@permission_required('bookshelf.can_bulk_operations', raise_exception=True)
@login_required
def bulk_operations(request):
    """
    View for bulk operations on books in bookshelf app.
    Requires 'can_bulk_operations' permission - typically for Admins only.
    Demonstrates permission enforcement with raise_exception=True.
    """
    books = Book.objects.all()
    
    if request.method == 'POST':
        selected_books = request.POST.getlist('selected_books')
        action = request.POST.get('action')
        
        if action == 'delete' and selected_books:
            deleted_count = Book.objects.filter(id__in=selected_books).count()
            Book.objects.filter(id__in=selected_books).delete()
            messages.success(request, f'Successfully deleted {deleted_count} books.')
        elif action == 'update_year' and selected_books:
            new_year = request.POST.get('new_year')
            if new_year:
                try:
                    updated_count = Book.objects.filter(id__in=selected_books).update(
                        publication_year=int(new_year)
                    )
                    messages.success(request, f'Successfully updated {updated_count} books.')
                except ValueError:
                    messages.error(request, 'Please enter a valid year.')
        
        return redirect('bookshelf:book_list')
    
    context = {
        'books': books,
        'title': 'Bulk Operations - Bookshelf',
    }
    return render(request, 'bookshelf/bulk_operations.html', context)

# Additional permission-protected helper views

@permission_required('bookshelf.can_view_all_books', raise_exception=True)
def search_books(request):
    """
    Search functionality for books with permission protection.
    Requires 'can_view_all_books' permission with raise_exception=True.
    """
    query = request.GET.get('q', '')
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            title__icontains=query
        ) | books.filter(
            author__icontains=query
        )
    
    context = {
        'books': books,
        'query': query,
        'title': f'Search Results for "{query}"' if query else 'Search Books',
    }
    return render(request, 'bookshelf/search_results.html', context)