"""
Django management command to set up user groups and assign permissions.
Step 2: Create and Configure Groups with Assigned Permissions

Usage: python manage.py setup_groups_permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from relationship_app.models import Book, Library

class Command(BaseCommand):
    help = 'Set up user groups and assign permissions for the LibraryProject'

    def handle(self, *args, **options):
        """
        Step 2: Create and Configure Groups with Assigned Permissions
        
        This command creates three main groups:
        - Viewers: Can only view books and basic information
        - Editors: Can view, create, and edit books  
        - Admins: Full permissions including delete and bulk operations
        """
        
        self.stdout.write(self.style.SUCCESS('Setting up groups and permissions...'))
        
        # Get content types for our models
        book_content_type = ContentType.objects.get_for_model(Book)
        library_content_type = ContentType.objects.get_for_model(Library)
        
        # Get all book-related permissions
        book_permissions = Permission.objects.filter(content_type=book_content_type)
        library_permissions = Permission.objects.filter(content_type=library_content_type)
        
        # Create or get the Viewers group
        viewers_group, created = Group.objects.get_or_create(name='Viewers')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Viewers group'))
        
        # Assign permissions to Viewers group
        viewers_permissions = [
            'can_view',              # Can view individual books
            'can_view_all_books',    # Can view book lists
        ]
        
        for permission_codename in viewers_permissions:
            try:
                permission = Permission.objects.get(
                    codename=permission_codename,
                    content_type=book_content_type
                )
                viewers_group.permissions.add(permission)
                self.stdout.write(f'Added {permission_codename} to Viewers group')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {permission_codename} not found')
                )
        
        # Create or get the Editors group
        editors_group, created = Group.objects.get_or_create(name='Editors')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Editors group'))
        
        # Assign permissions to Editors group
        editors_permissions = [
            'can_view',              # Can view books
            'can_view_all_books',    # Can view all books
            'can_create',            # Can create new books
            'can_edit',              # Can edit existing books
            'can_manage_authors',    # Can manage book authors
            'can_manage_library',    # Can manage libraries
        ]
        
        for permission_codename in editors_permissions:
            try:
                if permission_codename in ['can_manage_library']:
                    permission = Permission.objects.get(
                        codename=permission_codename,
                        content_type=library_content_type
                    )
                else:
                    permission = Permission.objects.get(
                        codename=permission_codename,
                        content_type=book_content_type
                    )
                editors_group.permissions.add(permission)
                self.stdout.write(f'Added {permission_codename} to Editors group')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {permission_codename} not found')
                )
        
        # Create or get the Admins group
        admins_group, created = Group.objects.get_or_create(name='Admins')
        if created:
            self.stdout.write(self.style.SUCCESS('Created Admins group'))
        
        # Assign all permissions to Admins group
        admins_permissions = [
            'can_view',                 # Can view books
            'can_view_all_books',       # Can view all books
            'can_create',               # Can create books
            'can_edit',                 # Can edit books
            'can_delete',               # Can delete books
            'can_manage_authors',       # Can manage authors
            'can_bulk_operations',      # Can perform bulk operations
            'can_manage_library',       # Can manage libraries
            'can_view_library_stats',   # Can view library statistics
        ]
        
        for permission_codename in admins_permissions:
            try:
                if permission_codename in ['can_manage_library', 'can_view_library_stats']:
                    permission = Permission.objects.get(
                        codename=permission_codename,
                        content_type=library_content_type
                    )
                else:
                    permission = Permission.objects.get(
                        codename=permission_codename,
                        content_type=book_content_type
                    )
                admins_group.permissions.add(permission)
                self.stdout.write(f'Added {permission_codename} to Admins group')
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {permission_codename} not found')
                )
        
        self.stdout.write(self.style.SUCCESS('\nGroups and permissions setup completed!'))
        self.stdout.write('\nGroup Summary:')
        self.stdout.write(f'- Viewers: {viewers_group.permissions.count()} permissions')
        self.stdout.write(f'- Editors: {editors_group.permissions.count()} permissions')
        self.stdout.write(f'- Admins: {admins_group.permissions.count()} permissions')
        
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Run migrations: python manage.py makemigrations && python manage.py migrate')
        self.stdout.write('2. Create test users and assign them to groups via Django admin')
        self.stdout.write('3. Test permissions by logging in as different users')