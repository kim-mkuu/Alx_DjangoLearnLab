from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Book, Library

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