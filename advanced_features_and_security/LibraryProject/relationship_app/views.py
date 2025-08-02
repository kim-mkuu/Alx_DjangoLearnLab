from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .models import Book, Library, Author
from .forms import BookForm

def home(request):
    """
    Home page view that renders the main page of the LibraryProject.
    """
    libraries = Library.objects.all()
    return render(request, 'relationship_app/home.html', {'libraries': libraries})

# Step 3: Enforce Permissions in Views - Book List View
@permission_required('relationship_app.can_view_all_books', raise_exception=True)
def list_books(request):
    """
    Function-based view that displays a list of all books in the database.
    Requires 'can_view_all_books' permission to access.
    """
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Permission-protected Book Detail View
@permission_required('relationship_app.can_view', raise_exception=True)
def book_detail(request, book_id):
    """
    View to display individual book details.
    Requires 'can_view' permission.
    """
    book = get_object_or_404(Book, id=book_id)
    context = {
        'book': book,
        'can_edit': request.user.has_perm('relationship_app.can_edit'),
        'can_delete': request.user.has_perm('relationship_app.can_delete'),
    }
    return render(request, 'relationship_app/book_detail.html', context)

class LibraryDetailView(DetailView):
    """
    Class-based view that displays details for a specific library.
    Shows library name and all books available in that library.
    """
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.
        Includes permission checks for library management.
        """
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()
        context['can_manage_library'] = self.request.user.has_perm('relationship_app.can_manage_library')
        return context

def register_view(request):
    """
    User registration view using Django's built-in UserCreationForm.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            messages.success(request, f'Account created for {username}! You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'relationship_app/register.html', {'form': form})

# Helper functions to check user roles
def is_admin(user):
    """Check if user has Admin role"""
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Admin'

def is_librarian(user):
    """Check if user has Librarian role"""
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Librarian'

def is_member(user):
    """Check if user has Member role"""
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Member'

# Enhanced role-based views with permission checks
@user_passes_test(is_admin)
@permission_required('relationship_app.can_view_library_stats', raise_exception=True)
def admin_view(request):
    """
    Admin view - Accessible to Admin role users with library stats permission.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'total_books': Book.objects.count(),
        'total_libraries': Library.objects.count(),
        'total_authors': Author.objects.count(),
        'can_bulk_operations': request.user.has_perm('relationship_app.can_bulk_operations'),
    }
    return render(request, 'relationship_app/admin_view.html', context)

@user_passes_test(is_librarian)
@permission_required('relationship_app.can_manage_library', raise_exception=True)
def librarian_view(request):
    """
    Librarian view - Accessible to Librarian role with library management permission.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'books': Book.objects.all(),
        'libraries': Library.objects.all(),
        'can_edit_books': request.user.has_perm('relationship_app.can_edit'),
        'can_create_books': request.user.has_perm('relationship_app.can_create'),
    }
    return render(request, 'relationship_app/librarian_view.html', context)

@user_passes_test(is_member)
@permission_required('relationship_app.can_view', raise_exception=True)
def member_view(request):
    """
    Member view - Accessible to Member role with basic view permission.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'available_books': Book.objects.all()[:10],  # Limited view for members
    }
    return render(request, 'relationship_app/member_view.html', context)

# Step 3: Permission-protected CRUD Views with Enhanced Security

@permission_required('relationship_app.can_create', raise_exception=True)
@login_required
def add_book(request):
    """
    View to add a new book. 
    Requires 'can_create' permission - typically assigned to Editors and Admins groups.
    """
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been added successfully!')
            return redirect('list_books')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm()
    
    context = {
        'form': form,
        'title': 'Add New Book',
        'submit_text': 'Add Book'
    }
    return render(request, 'relationship_app/book_form.html', context)

@permission_required('relationship_app.can_edit', raise_exception=True)
@login_required
def edit_book(request, book_id):
    """
    View to edit an existing book. 
    Requires 'can_edit' permission - typically assigned to Editors and Admins groups.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            updated_book = form.save()
            messages.success(request, f'Book "{updated_book.title}" has been updated successfully!')
            return redirect('list_books')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookForm(instance=book)
    
    context = {
        'form': form,
        'book': book,
        'title': f'Edit Book: {book.title}',
        'submit_text': 'Update Book'
    }
    return render(request, 'relationship_app/book_form.html', context)

@permission_required('relationship_app.can_delete', raise_exception=True)
@login_required
def delete_book(request, book_id):
    """
    View to delete a book. 
    Requires 'can_delete' permission - typically assigned to Admins group only.
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        book_title = book.title
        book.delete()
        messages.success(request, f'Book "{book_title}" has been deleted successfully!')
        return redirect('list_books')
    
    context = {
        'book': book,
        'title': f'Delete Book: {book.title}'
    }
    return render(request, 'relationship_app/book_confirm_delete.html', context)

# Additional permission-protected views

@permission_required('relationship_app.can_manage_authors', raise_exception=True)
@login_required
def manage_authors(request):
    """
    View to manage book authors.
    Requires 'can_manage_authors' permission - typically for Editors and Admins.
    """
    authors = Author.objects.all()
    context = {
        'authors': authors,
        'title': 'Manage Authors'
    }
    return render(request, 'relationship_app/manage_authors.html', context)

@permission_required('relationship_app.can_bulk_operations', raise_exception=True)
@login_required
def bulk_operations(request):
    """
    View for bulk operations on books.
    Requires 'can_bulk_operations' permission - typically for Admins only.
    """
    if request.method == 'POST':
        selected_books = request.POST.getlist('selected_books')
        action = request.POST.get('action')
        
        if action == 'delete' and selected_books:
            deleted_count = Book.objects.filter(id__in=selected_books).count()
            Book.objects.filter(id__in=selected_books).delete()
            messages.success(request, f'Successfully deleted {deleted_count} books.')
        
        return redirect('list_books')
    
    books = Book.objects.all()
    context = {
        'books': books,
        'title': 'Bulk Operations'
    }
    return render(request, 'relationship_app/bulk_operations.html', context)