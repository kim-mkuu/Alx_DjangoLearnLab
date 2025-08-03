from rest_framework import generics, viewsets
from .models import Book
from .serializers import BookSerializer

#BookList View
class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

#BookViewSet for full CRUD operations
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all
    serializer_class = BookSerializer
