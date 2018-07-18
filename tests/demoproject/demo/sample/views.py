from demo.sample import serializers
from demo.sample.models import Author, Book
from rest_framework import viewsets


class AuthorView(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer
