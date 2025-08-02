"""
Django management command to create test users and demonstrate permissions.
Step 4: Test Permissions

Usage: python manage.py test_permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from relationship_app.models import UserProfile, Author, Book

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users and demonstrate permissions system'

    def handle(self, *args, **options):
        """
        Step 4: Test Permissions
        
        Creates test users and assigns them to different groups to demonstrate
        the permissions system in action.
        """
        
        self.stdout.write(self.style.SUCCESS('Creating test users for permissions testing...'))
        
        # Ensure groups exist
        try:
            viewers_group = Group.objects.get(name='Viewers')
            editors_group = Group.objects.get(name='Editors')
            admins_group = Group.objects.get(name='Admins')
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Groups not found. Please run: python manage.py setup_groups_permissions')
            )
            return
        
        # Create test users
        test_users = [
            {
                'username': 'viewer_user',
                'email': 'viewer@library.com',
                'password': 'testpass123',
                'group': viewers_group,
                'role': 'Member'
            },
            {
                'username': 'editor_user',
                'email': 'editor@library.com',
                'password': 'testpass123',
                'group': editors_group,
                'role': 'Librarian'
            },
            {
                'username': 'admin_user',
                'email': 'admin@library.com',
                'password': 'testpass123',
                'group': admins_group,
                'role': 'Admin'
            }
        ]
        
        for user_data in test_users:
            # Create or get user
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['username'].replace('_', ' ').title(),
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User already exists: {user.username}')
            
            # Assign to group
            user.groups.clear()  # Remove from all groups first
            user.groups.add(user_data['group'])
            
            # Update UserProfile role
            if hasattr(user, 'userprofile'):
                user.userprofile.role = user_data['role']
                user.userprofile.save()
            else:
                UserProfile.objects.create(user=user, role=user_data['role'])
            
            self.stdout.write(f'Assigned {user.username} to {user_data["group"].name} group with {user_data["role"]} role')
        
        # Create sample data for testing
        self.create_sample_data()
        
        # Display permission testing guide
        self.display_testing_guide()
    
    def create_sample_data(self):
        """Create sample authors and books for testing"""
        self.stdout.write('\nCreating sample data...')
        
        # Create sample authors
        authors_data = [
            'J.K. Rowling',
            'George Orwell',
            'Harper Lee'
        ]
        
        for author_name in authors_data:
            author, created = Author.objects.get_or_create(name=author_name)
            if created:
                self.stdout.write(f'Created author: {author.name}')
        
        # Create sample books
        books_data = [
            {'title': 'Harry Potter and the Philosopher\'s Stone', 'author': 'J.K. Rowling', 'year': 1997},
            {'title': '1984', 'author': 'George Orwell', 'year': 1949},
            {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'year': 1960},
        ]
        
        for book_data in books_data:
            author = Author.objects.get(name=book_data['author'])
            book, created = Book.objects.get_or_create(
                title=book_data['title'],
                defaults={
                    'author': author,
                    'publication_year': book_data['year']
                }
            )
            if created:
                self.stdout.write(f'Created book: {book.title}')
    
    def display_testing_guide(self):
        """Display testing instructions"""
        self.stdout.write(self.style.SUCCESS('\nTest Users Created Successfully!'))
        self.stdout.write('\n' + '='*60)
        self.stdout.write('PERMISSIONS TESTING GUIDE')
        self.stdout.write('='*60)
        
        self.stdout.write('\nTest Users and Credentials:')
        self.stdout.write('-' * 30)
        self.stdout.write('1. Viewer User:')
        self.stdout.write('   Username: viewer_user')
        self.stdout.write('   Password: testpass123') 
        self.stdout.write('   Group: Viewers')
        self.stdout.write('   Permissions: can_view, can_view_all_books')
        
        self.stdout.write('\n2. Editor User:')
        self.stdout.write('   Username: editor_user')
        self.stdout.write('   Password: testpass123')
        self.stdout.write('   Group: Editors') 
        self.stdout.write('   Permissions: can_view, can_view_all_books, can_create, can_edit, can_manage_authors')
        
        self.stdout.write('\n3. Admin User:')
        self.stdout.write('   Username: admin_user')
        self.stdout.write('   Password: testpass123')
        self.stdout.write('   Group: Admins')
        self.stdout.write('   Permissions: All permissions including can_delete, can_bulk_operations')
        
        self.stdout.write('\nTesting Steps:')
        self.stdout.write('-' * 15)
        self.stdout.write('1. Start the development server: python manage.py runserver')
        self.stdout.write('2. Navigate to http://127.0.0.1:8000/')
        self.stdout.write('3. Log in as each test user and try accessing:')
        self.stdout.write('   - /books/ (View all books)')
        self.stdout.write('   - /add_book/ (Add new book)')
        self.stdout.write('   - /edit_book/<id>/ (Edit book)')
        self.stdout.write('   - /delete_book/<id>/ (Delete book)')
        self.stdout.write('   - /admin/ (Admin panel)')
        
        self.stdout.write('\nExpected Results:')
        self.stdout.write('-' * 17)
        self.stdout.write('• viewer_user: Can only view books, blocked from create/edit/delete')
        self.stdout.write('• editor_user: Can view, create, and edit books, blocked from delete')
        self.stdout.write('• admin_user: Full access to all operations')
        
        self.stdout.write('\n' + '='*60)