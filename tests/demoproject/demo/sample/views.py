from demo.sample import serializers
from demo.sample.models import Author, Book
from rest_framework import viewsets
from rest_framework.generics import ListAPIView

from unicef_restlib.pagination import DynamicPageNumberPagination
from unicef_restlib.permissions import IsSuperUser
from unicef_restlib.views import NestedViewSetMixin, QueryStringFilterAPIView


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


class AuthorView(QueryStringFilterAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = (IsSuperUser,)
    filters = (
        ('first_name', 'first_name'),
    )
    search_terms = ('first_name__istartswith',)
