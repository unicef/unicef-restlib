from demo.sample import serializers
from demo.sample.metadata import CRUMetadata, FSMMetadata
from demo.sample.models import Author, Book, Review
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView

from unicef_restlib.pagination import DynamicPageNumberPagination
from unicef_restlib.permissions import IsSuperUser
from unicef_restlib.views import (
    MultiSerializerViewSetMixin,
    NestedViewSetMixin,
    QueryStringFilterMixin,
    SafeTenantViewSetMixin,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class AuthorSafeTenantViewSet(SafeTenantViewSetMixin, viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer


class AuthorPaginateView(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    pagination_class = DynamicPageNumberPagination


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer


class BookFilterNestedViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    parent = AuthorViewSet
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def get_parent_filter(self):
        return {"author__active": True}


class BookNestedViewSet(MultiSerializerViewSetMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    parent = AuthorViewSet
    parent_lookup_field = "author"
    parent_lookup_kwarg = "author_pk"
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def perform_create(self, serializer, **kwargs):
        parent = self.get_parent_object()
        serializer.save(author=parent)


class BookRootNestedViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    parent = AuthorViewSet
    parent_lookup_field = "author"
    parent_lookup_kwarg = "author_pk"
    queryset = Book.objects.all()
    serializer_class = serializers.BookSerializer

    def perform_create(self, serializer, **kwargs):
        root = self.get_root_object()
        serializer.save(author=root)


class AuthorView(QueryStringFilterMixin, ListAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    permission_classes = (IsSuperUser,)
    filters = (
        ('first_name', 'first_name'),
    )
    search_terms = ('first_name__istartswith',)


class AuthorMetaCRUView(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorMetaSerializer
    metadata_class = CRUMetadata


class AuthorMetaFSMListView(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorMetaSerializer
    metadata_class = FSMMetadata


class AuthorMetaFSMView(RetrieveUpdateAPIView):
    queryset = Author.objects.all()
    serializer_class = serializers.AuthorMetaSerializer
    metadata_class = FSMMetadata
    permission_classes = (IsSuperUser,)


class ReviewMetaFSMView(RetrieveUpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewMetaSerializer
    metadata_class = FSMMetadata
    permission_classes = (IsSuperUser,)
