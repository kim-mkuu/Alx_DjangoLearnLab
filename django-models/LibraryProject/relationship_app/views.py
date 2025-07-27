from django.shortcuts import render
from django.views.generic.detail import DetailView
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