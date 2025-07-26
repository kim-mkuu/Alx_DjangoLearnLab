from django.shortcuts import render
from django.views.generic import DetailView
from .models import Book, Library

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