from demo.sample import serializers
from demo.sample.models import Author, Book
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from unicef_restlib.pagination import DynamicPageNumberPagination
from unicef_restlib.views import NestedViewSetMixin


class AuthorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class AuthorPaginateView(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    pagination_class = DynamicPageNumberPagination


class BookViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    parent = Author
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def get_parent_filter(self):
        return {"author__active": True}
