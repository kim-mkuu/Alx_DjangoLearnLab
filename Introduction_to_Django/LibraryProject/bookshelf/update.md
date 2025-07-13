## 3. Update Operation

```python
book.title = "Nineteen Eighty-Four"
book.save()
updated_book = Book.objects.get(id=book.id)
print(updated_book.title)
```

**Output:**  
`Nineteen Eighty-Four`
