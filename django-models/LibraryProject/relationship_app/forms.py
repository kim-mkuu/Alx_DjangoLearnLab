from django import forms
from .models import Book, Author

class BookForm(forms.ModelForm):
    """
    Form for creating and updating Book instances.
    """
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'publication_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title',
                'required': True
            }),
            'author': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter publication year (e.g., 2023)',
                'min': 1000,
                'max': 2100,
                'required': True
            }),
        }
        labels = {
            'title': 'Book Title',
            'author': 'Author',
            'publication_year': 'Publication Year',
        }
        help_texts = {
            'title': 'Enter the full title of the book.',
            'author': 'Select the author from the dropdown.',
            'publication_year': 'Enter the year the book was published.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure we have authors available in the dropdown
        self.fields['author'].queryset = Author.objects.all().order_by('name')
        
        # Add empty option for author selection
        self.fields['author'].empty_label = "Select an author"

    def clean_publication_year(self):
        """
        Custom validation for publication year.
        """
        year = self.cleaned_data.get('publication_year')
        if year and (year < 1000 or year > 2100):
            raise forms.ValidationError('Please enter a valid publication year between 1000 and 2100.')
        return year

    def clean_title(self):
        """
        Custom validation for book title.
        """
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 2:
                raise forms.ValidationError('Book title must be at least 2 characters long.')
        return title