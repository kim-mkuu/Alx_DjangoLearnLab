from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

#Get the custom user model
User = get_user_model()

# Models creation for the relationship_app
class Author(models.Model):
    name = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publication_year = models.IntegerField()
    
    def __str__(self):
        return self.title
    
    class Meta:
        permissions = [
            #Step 1: Define Custom Permissions in models
            #These permissions control specific actions on Book instances 

            ("can_view", "Can view book"), #View book details
            ("can_create", "Can create book"),#Add new books
            ("can_edit", "Can edit book"),#Modify existing books
            ("can_delete", "Can delete book"),#Remove books

            # Additional granular permissions for enhanced control
            ("can_view_all_books", "Can view all books"),        # View complete book list
            ("can_manage_authors", "Can manage book authors"),   # Manage author assignments
            ("can_bulk_operations", "Can perform bulk operations"), # Bulk edit/delete 
        ]

        #Verbose names for better admin interface
        verbose_name = "Book"
        verbose_name_plural = "Books"

class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)
    
    def __str__(self):
        return self.name
    
    class Meta:
        permissions = [
            # Library-specific permissions
            ("can_manage_library", "Can manage library"),
            ("can_view_library_stats", "Can view library statistics"),
        ]

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.OneToOneField(Library, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

# UserProfile model for role-based access control
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Librarian', 'Librarian'),
        ('Member', 'Member'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Member')
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Django signal to automatically create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a new User is registered.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the UserProfile when the User is saved.
    """
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)