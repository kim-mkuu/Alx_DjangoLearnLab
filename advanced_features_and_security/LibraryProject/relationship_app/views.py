from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Book
from .models import Library
from .models import Author
from .forms import BookForm

def home(request):
    """
    Home page view that renders the main page(also link to other views if they exist) of the LibraryProject.
    """
    libraries = Library.objects.all()
    return render(request, 'relationship_app/home.html', {'libraries': libraries})

def list_books(request):
    """
    Function-based view that displays a list of all books in the database.
    Renders book titles and their authors.
    """
    books = Book.objects.all()
    return render(request, 'relationship_app/list_books.html', {'books': books})

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
        Ensures all books in the library are available in the template.
        """
        context = super().get_context_data(**kwargs)
        context['books'] = self.object.books.all()
        return context

def register_view(request):
    """
    User registration view using Django's built-in UserCreationForm.
    Handles both GET (display form) and POST (process form) requests.
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

# Role-based views with access control
@user_passes_test(is_admin)
def admin_view(request):
    """
    Admin view - Only accessible to users with Admin role.
    Displays admin-specific content and functionality.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'total_books': Book.objects.count(),
        'total_libraries': Library.objects.count(),
    }
    return render(request, 'relationship_app/admin_view.html', context)

@user_passes_test(is_librarian)
def librarian_view(request):
    """
    Librarian view - Only accessible to users with Librarian role.
    Displays librarian-specific content and functionality.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'books': Book.objects.all(),
        'libraries': Library.objects.all(),
    }
    return render(request, 'relationship_app/librarian_view.html', context)

@user_passes_test(is_member)
def member_view(request):
    """
    Member view - Only accessible to users with Member role.
    Displays member-specific content and functionality.
    """
    context = {
        'user': request.user,
        'role': request.user.userprofile.role,
        'available_books': Book.objects.all(),
    }
    return render(request, 'relationship_app/member_view.html', context)

# Custom permission-protected views for Book CRUD operations

@permission_required('relationship_app.can_add_book', raise_exception=True)
def add_book(request):
    """
    View to add a new book. Requires 'can_add_book' permission.
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

@permission_required('relationship_app.can_change_book', raise_exception=True)
def edit_book(request, book_id):
    """
    View to edit an existing book. Requires 'can_change_book' permission.
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

@permission_required('relationship_app.can_delete_book', raise_exception=True)
def delete_book(request, book_id):
    """
    View to delete a book. Requires 'can_delete_book' permission.
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