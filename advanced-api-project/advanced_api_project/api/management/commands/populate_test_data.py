"""
Management command to populate the database with test data.

This command creates sample authors and books for testing the API
and serializers functionality.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Author, Book
import random


class Command(BaseCommand):
    help = 'Populate the database with test data for authors and books'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--authors',
            type=int,
            default=5,
            help='Number of authors to create (default: 5)'
        )
        parser.add_argument(
            '--books-per-author',
            type=int,
            default=3,
            help='Average number of books per author (default: 3)'
        )
    
    def handle(self, *args, **options):
        authors_count = options['authors']
        books_per_author = options['books_per_author']
        
        # Sample data
        author_names = [
            'Jane Austen', 'Charles Dickens', 'Mark Twain', 'Virginia Woolf',
            'Ernest Hemingway', 'F. Scott Fitzgerald', 'George Orwell',
            'Agatha Christie', 'J.K. Rowling', 'Stephen King'
        ]
        
        # Different book titles for each author to avoid confusion
        book_titles_by_author = {
            'Jane Austen': [
                'Pride and Prejudice', 'Emma', 'Sense and Sensibility', 
                'Mansfield Park', 'Northanger Abbey', 'Persuasion'
            ],
            'Charles Dickens': [
                'Great Expectations', 'Oliver Twist', 'A Tale of Two Cities',
                'David Copperfield', 'Bleak House', 'Hard Times'
            ],
            'Mark Twain': [
                'The Adventures of Tom Sawyer', 'Adventures of Huckleberry Finn',
                'The Prince and the Pauper', 'A Connecticut Yankee', 'Tom Sawyer Abroad'
            ],
            'Virginia Woolf': [
                'Mrs Dalloway', 'To the Lighthouse', 'Orlando',
                'The Waves', 'The Years', 'Between the Acts'
            ],
            'Ernest Hemingway': [
                'The Sun Also Rises', 'A Farewell to Arms', 'For Whom the Bell Tolls',
                'The Old Man and the Sea', 'Islands in the Stream'
            ],
            'F. Scott Fitzgerald': [
                'The Great Gatsby', 'Tender Is the Night', 'This Side of Paradise',
                'The Beautiful and Damned', 'The Last Tycoon'
            ],
            'George Orwell': [
                '1984', 'Animal Farm', 'Homage to Catalonia',
                'The Road to Wigan Pier', 'Burmese Days'
            ],
            'Agatha Christie': [
                'Murder on the Orient Express', 'The Murder of Roger Ackroyd',
                'And Then There Were None', 'Death on the Nile', 'The ABC Murders'
            ],
            'J.K. Rowling': [
                'Harry Potter and the Philosopher\'s Stone', 'Harry Potter and the Chamber of Secrets',
                'Harry Potter and the Prisoner of Azkaban', 'The Casual Vacancy'
            ],
            'Stephen King': [
                'The Shining', 'It', 'Carrie', 'Pet Sematary',
                'The Stand', 'Misery', 'Salem\'s Lot'
            ]
        }
        
        # Generic titles as fallback
        generic_titles = [
            'The Great Adventure', 'Mystery of the Old House', 'Journey to Tomorrow',
            'The Lost City', 'Secrets of the Past', 'The Final Chapter',
            'Whispers in the Dark', 'The Golden Key', 'Tales of Wonder',
            'The Silent Observer', 'Dreams and Shadows', 'The Crystal Lake',
            'Echoes of Time', 'The Forgotten Path', 'Midnight Stories'
        ]
        
        with transaction.atomic():
            # Clear existing data
            Book.objects.all().delete()
            Author.objects.all().delete()
            
            created_authors = []
            
            # Create authors
            for i in range(authors_count):
                author_name = author_names[i % len(author_names)]
                
                # If we need more authors than available names, add numbers
                if i >= len(author_names):
                    author_name = f"{author_name} {i - len(author_names) + 2}"
                
                author = Author.objects.create(name=author_name)
                created_authors.append(author)
                self.stdout.write(
                    self.style.SUCCESS(f'Created author: {author.name}')
                )
            
            # Create books for each author
            for author in created_authors:
                self.stdout.write(f'Creating books for {author.name}:')
                
                # Get specific titles for this author or use generic ones
                if author.name in book_titles_by_author:
                    available_titles = book_titles_by_author[author.name].copy()
                else:
                    available_titles = generic_titles.copy()
                
                # Randomize the number of books for variety
                num_books = random.randint(max(1, books_per_author - 1), books_per_author + 2)
                num_books = min(num_books, len(available_titles))  # Don't exceed available titles
                
                # Shuffle titles and take the required number
                random.shuffle(available_titles)
                selected_titles = available_titles[:num_books]
                
                for title in selected_titles:
                    year = random.randint(1950, 2023)
                    
                    try:
                        book = Book.objects.create(
                            title=title,
                            publication_year=year,
                            author=author
                        )
                        self.stdout.write(
                            self.style.SUCCESS(f'  Created book: {book.title} ({year})')
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  Failed to create book "{title}": {e}')
                        )
            
            # Display summary
            total_authors = Author.objects.count()
            total_books = Book.objects.count()
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {total_authors} authors and {total_books} books!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Average books per author: {total_books / total_authors:.1f}'
                )
            )