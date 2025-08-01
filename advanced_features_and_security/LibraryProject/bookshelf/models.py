from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for CustomUser model.
    Handles user creation with additional fields.
    """
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a regular user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and return a superuser with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds additional fields for enhanced user profile management.
    """
    
    # Additional custom fields
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="User's date of birth"
    )
    
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        help_text="User's profile photo"
    )
    
    # Required fields for user creation
    email = models.EmailField(unique=True)
    
    # Use custom manager
    objects = CustomUserManager()
    
    # Specify required fields for createsuperuser command
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        
    def __str__(self):
        return self.username
    
    @property
    def age(self):
        """Calculate user's age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

# Keep the existing Book model from bookshelf app
class Book(models.Model):
    """
    Represents a book with a title, author, and publication year.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()
    
    def __str__(self):
        return f"{self.title} by {self.author} ({self.publication_year})"