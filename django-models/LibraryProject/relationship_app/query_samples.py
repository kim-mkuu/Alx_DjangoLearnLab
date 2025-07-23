#!/usr/bin/env python

# (#!hashbang)  makes script work regardless of where python is installed, as long as it's in the PATH. 
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def create_sample_data():
    """Create sample data for testing relationships"""
    print("Creating sample data...")
    
    # Clear existing data to avoid duplicates
    print("Clearing existing data...")
    Librarian.objects.all().delete()
    Library.objects.all().delete()
    Book.objects.all().delete()
    Author.objects.all().delete()
    
    # Create authors
    author1 = Author.objects.create(name="George Orwell")
    author2 = Author.objects.create(name="J.K. Rowling")
    author3 = Author.objects.create(name="Harper Lee")
    print(f"Created authors: {author1}, {author2}, {author3}")
    
    # Create books with ForeignKey relationships
    book1 = Book.objects.create(title="1984", author=author1)
    book2 = Book.objects.create(title="Animal Farm", author=author1)
    book3 = Book.objects.create(title="Harry Potter and the Philosopher's Stone", author=author2)
    book4 = Book.objects.create(title="To Kill a Mockingbird", author=author3)
    print(f"Created books: {book1}, {book2}, {book3}, {book4}")
    
    # Create libraries
    library1 = Library.objects.create(name="Central Library")
    library2 = Library.objects.create(name="Community Library")
    print(f"Created libraries: {library1}, {library2}")
    
    # Add books to libraries (ManyToMany relationships)
    library1.books.add(book1, book2, book3)  # Central Library has 3 books
    library2.books.add(book3, book4)         # Community Library has 2 books
    print("Added books to libraries (ManyToMany relationships)")
    
    # Create librarians with OneToOne relationships
    librarian1 = Librarian.objects.create(name="John Smith", library=library1)
    librarian2 = Librarian.objects.create(name="Jane Doe", library=library2)
    print(f"Created librarians: {librarian1}, {librarian2}")
    
    print("Sample data creation completed!\n")
    return author1, author2, author3, library1, library2

def query_books_by_author(author_name):
    """Query all books by a specific author (ForeignKey relationship)"""
    try:
        author = Author.objects.get(name=author_name)
        books = Book.objects.filter(author=author)
        return books
    except Author.DoesNotExist:
        print(f"Author '{author_name}' not found!")
        return None

def list_books_in_library(library_name):
    """List all books in a library (ManyToMany relationship)"""
    try:
        library = Library.objects.get(name=library_name)
        books = library.books.all()
        return books
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found!")
        return None

def get_librarian_for_library(library_name):
    """Retrieve the librarian for a library (OneToOne relationship)"""
    try:
        library = Library.objects.get(name=library_name)
        librarian = Librarian.objects.get(library=library)
        return librarian
    except Library.DoesNotExist:
        print(f"Library '{library_name}' not found!")
        return None
    except Librarian.DoesNotExist:
        print(f"No librarian found for library '{library_name}'!")
        return None

def test_all_relationships():
    """Test all three types of Django relationships"""
    print("=" * 60)
    print("TESTING DJANGO RELATIONSHIPS")
    print("=" * 60)
    
    # Create sample data first
    author1, author2, author3, library1, library2 = create_sample_data()
    
    # QUERY 1: Query all books by a specific author (ForeignKey Relationship)
    print("QUERY 1: Query all books by a specific author")
    print("-" * 50)
    books_by_orwell = query_books_by_author("George Orwell")
    if books_by_orwell:
        print(f"Books by George Orwell:")
        for book in books_by_orwell:
            print(f"  {book.title}")
    print()

    books_by_rowling = query_books_by_author("J.K. Rowling")
    if books_by_rowling:
        print(f"Books by J.K. Rowling:")
        for book in books_by_rowling:
            print(f"  {book.title}")
    print()
    
    books_by_lee = query_books_by_author("Harper Lee")
    if books_by_lee:
        print(f"Books by Harper Lee:")
        for book in books_by_lee:
            print(f"  {book.title}")
    print()
    
    # QUERY 2: List all books in a library (ManyToMany Relationship)
    print("QUERY 2: List all books in a library")
    print("-" * 50)
    central_books = list_books_in_library("Central Library")
    if central_books:
        print(f"Books in Central Library:")
        for book in central_books:
            print(f"  {book.title}")
    
    # Also test another library
    community_books = list_books_in_library("Community Library")
    if community_books:
        print(f"Books in Community Library:")
        for book in community_books:
            print(f"  {book.title}")
    print()
    
    # QUERY 3: Retrieve the librarian for a library (OneToOne Relationship)
    print("QUERY 3: Retrieve the librarian for a library")
    print("-" * 50)
    librarian1 = get_librarian_for_library("Central Library")
    if librarian1:
        print(f"Librarian for Central Library: {librarian1.name}")
    
    librarian2 = get_librarian_for_library("Community Library")
    if librarian2:
        print(f"Librarian for Community Library: {librarian2.name}")
    print()
    
    # Final Summary
    print("SUMMARY")
    print("-" * 20)
    print(f"Total Authors: {Author.objects.count()}")
    print(f"Total Books: {Book.objects.count()}")
    print(f"Total Libraries: {Library.objects.count()}")
    print(f"Total Librarians: {Librarian.objects.count()}")
    
    print("\nAll relationship tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_all_relationships()