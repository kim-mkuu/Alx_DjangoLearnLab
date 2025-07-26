from django.db import models

# Models creation for the relationship_app
class Author(models.Model):
    name = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name
    """
    Admin interface for managing Author model.
    """

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publication_year = models.IntegerField()
    
    def __str__(self):
        return self.title
    """
    Admin interface for managing Book model.
    """

class Library(models.Model):
    name = models.CharField(max_length=100)
    books = models.ManyToManyField(Book)
    
    def __str__(self):
        return self.name
    """Admin interface for managing Library model.
    """

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    library = models.OneToOneField(Library, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    """Admin interface for managing Librarian model.
    """