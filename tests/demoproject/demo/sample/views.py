from demo.sample import serializers
from demo.sample.models import Author, Book
from rest_framework import viewsets

from unicef_restlib.views import NestedViewSetMixin


class AuthorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class BookViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    parent = "author"
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def get_parent_filter(self):
        return {"author__active": True}
