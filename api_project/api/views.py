from rest_framework import generics, viewsets, permissions
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):
    """
    List all books - requires authentication
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookViewSet(viewsets.ModelViewSet):
    """
    Full CRUD operations for books with different permission levels:
    - Read operations: Any authenticated user
    - Write operations: Admin users only
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            # Read operations - any authenticated user
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Write operations (create, update, destroy) - admin only
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]