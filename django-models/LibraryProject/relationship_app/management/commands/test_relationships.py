from django.core.management.base import BaseCommand
from relationship_app.models import Author, Book, Library, Librarian

class Command(BaseCommand):
    help = 'Test relationship models by creating sample data and running queries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting relationship tests...'))
        
        # Clear existing data (optional)
        self.stdout.write('Clearing existing data...')
        Librarian.objects.all().delete()
        Library.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()
        
        # Step 1: Create Authors
        self.stdout.write('\n1. Creating Authors...')
        author1 = Author.objects.create(name="George Orwell")
        author2 = Author.objects.create(name="J.K. Rowling")
        author3 = Author.objects.create(name="Harper Lee")
        
        self.stdout.write(f"   Created: {author1}")
        self.stdout.write(f"   Created: {author2}")
        self.stdout.write(f"   Created: {author3}")
        
        # Step 2: Create Books (ForeignKey relationship)
        self.stdout.write('\n2. Creating Books with Author relationships...')
        book1 = Book.objects.create(title="1984", author=author1)
        book2 = Book.objects.create(title="Animal Farm", author=author1)
        book3 = Book.objects.create(title="Harry Potter and the Philosopher's Stone", author=author2)
        book4 = Book.objects.create(title="To Kill a Mockingbird", author=author3)
        
        self.stdout.write(f"   Created: {book1} by {book1.author}")
        self.stdout.write(f"   Created: {book2} by {book2.author}")
        self.stdout.write(f"   Created: {book3} by {book3.author}")
        self.stdout.write(f"   Created: {book4} by {book4.author}")
        
        # Step 3: Create Libraries
        self.stdout.write('\n3. Creating Libraries...')
        library1 = Library.objects.create(name="Central Library")
        library2 = Library.objects.create(name="Community Library")
        
        self.stdout.write(f"   Created: {library1}")
        self.stdout.write(f"   Created: {library2}")
        
        # Step 4: Add Books to Libraries (ManyToMany relationship)
        self.stdout.write('\n4. Adding Books to Libraries (ManyToMany)...')
        library1.books.add(book1, book2, book3)
        library2.books.add(book3, book4)
        
        self.stdout.write(f"   Added 3 books to {library1}")
        self.stdout.write(f"   Added 2 books to {library2}")
        
        # Step 5: Create Librarians (OneToOne relationship)
        self.stdout.write('\n5. Creating Librarians (OneToOne with Libraries)...')
        librarian1 = Librarian.objects.create(name="John Smith", library=library1)
        librarian2 = Librarian.objects.create(name="Jane Doe", library=library2)
        
        self.stdout.write(f"   Created: {librarian1} at {librarian1.library}")
        self.stdout.write(f"   Created: {librarian2} at {librarian2.library}")
        
        # Test Queries
        self.stdout.write(self.style.SUCCESS('\n=== TESTING RELATIONSHIPS ==='))
        
        # Test 1: ForeignKey - Books by Author
        self.stdout.write('\nTest 1: Books by George Orwell (ForeignKey)')
        orwell_books = Book.objects.filter(author=author1)
        for book in orwell_books:
            self.stdout.write(f"   - {book.title}")
        
        # Test 2: ManyToMany - Books in Library
        self.stdout.write('\nTest 2: Books in Central Library (ManyToMany)')
        central_books = library1.books.all()
        for book in central_books:
            self.stdout.write(f"   - {book.title}")
        
        # Test 3: OneToOne - Librarian for Library
        self.stdout.write('\nTest 3: Librarian for Central Library (OneToOne)')
        central_librarian = library1.librarian
        self.stdout.write(f"   - {central_librarian.name}")
        
        # Additional Tests
        self.stdout.write('\n=== ADDITIONAL RELATIONSHIP TESTS ===')
        
        # Reverse ForeignKey lookup
        self.stdout.write('\nReverse lookup - All books by each author:')
        for author in Author.objects.all():
            books = author.book_set.all()
            self.stdout.write(f"   {author.name}: {[book.title for book in books]}")
        
        # Reverse ManyToMany lookup
        self.stdout.write('\nWhich libraries contain Harry Potter:')
        hp_libraries = book3.library_set.all()
        for library in hp_libraries:
            self.stdout.write(f"   - {library.name}")
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SUMMARY ==='))
        self.stdout.write(f"Total Authors: {Author.objects.count()}")
        self.stdout.write(f"Total Books: {Book.objects.count()}")
        self.stdout.write(f"Total Libraries: {Library.objects.count()}")
        self.stdout.write(f"Total Librarians: {Librarian.objects.count()}")
        
        self.stdout.write(self.style.SUCCESS('\nRelationship tests completed successfully!'))