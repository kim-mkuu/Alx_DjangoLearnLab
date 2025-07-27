from django.shortcuts import render, redirect
from django.views.generic.detail import DetailView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from .models import Library

def home(request):
    """
    Home page view that renders the main page(also link to other views if they exist) of the LibraryProject.
    """
    libraries = Library.objects.all()
    return render(request, 'relationship_app/home.html', {'libraries': libraries})

#Function-based view to list all books
def list_books(request):
    """
    Function-based view that displays a list of all books in the database.
    Renders book titles and their authors.
    """

    books = Book.objects.all() #Get all books from database
    return render(request, 'relationship_app/list_books.html', {'books': books} )

# Class-based view to display library details
class LibraryDetailView(DetailView):
    """"
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
        #Explicitly add books to context.
        context['books'] = self.object.books.all()
        return context
    
#Authentication views
def register_view(request):
    """
    View to handle user registration.
    Uses Django's built-in UserCreationForm for user registration.
    Handles both GET (display form) and POST (process form) requests.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'relationship_app/register.html', {'form': form})

def login_view(request):
    """
    User login view using Django's built-in AuthenticationForm.
    Authenticates user and creates session upon successful login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect to next page if specified, otherwise to home
                next_page = request.GET.get('next', 'home')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'relationship_app/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    User logout view that ends the user session.
    Requires user to be logged in (@login_required decorator).
    """
    username = request.user.username
    logout(request)
    messages.success(request, f'You have been logged out successfully, {username}!')
    return render(request, 'relationship_app/logout.html')