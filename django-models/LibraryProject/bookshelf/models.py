from django.db import models

#Defining the model
class Book(models.Model):
    """
    Represents a book with a title, author, and publication year.
    """
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    publication_year = models.IntegerField()

    def __str__(self):
        """
        String representation of the Book model, useful for admin and debugging.
        """
        return f"{self.title} by {self.author} ({self.publication_year})"
