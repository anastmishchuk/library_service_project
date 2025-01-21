from rest_framework import viewsets

from catalog.models import Book
from catalog.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
