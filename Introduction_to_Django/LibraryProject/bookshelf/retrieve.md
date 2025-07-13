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
