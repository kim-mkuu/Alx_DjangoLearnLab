# CRUD Operations Documentation

## 1. Create Operation

```python
from bookshelf.models import Book
book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)
print(book)
```

**Output:**  
`<Book: 1984>`

## 2. Retrieve Operation

```python
book = Book.objects.get(title="1984")
print(f"Title: {book.title}")
print(f"Author: {book.author}")
print(f"Year: {book.publication_year}")
```

**Output:**

```
Title: 1984
Author: George Orwell
Year: 1949
```

## 3. Update Operation

```python
book.title = "Nineteen Eighty-Four"
book.save()
updated_book = Book.objects.get(id=book.id)
print(updated_book.title)
```

**Output:**  
`Nineteen Eighty-Four`

## 4. Delete Operation

```python
book.delete()
print(Book.objects.all())
```

**Output:**  
`<QuerySet []>`
