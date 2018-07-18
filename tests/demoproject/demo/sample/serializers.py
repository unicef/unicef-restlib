from demo.sample.models import Activity, Author, Book, Image, ISBN, Review
from rest_framework import serializers

from unicef_restlib.fields import SeparatedReadWriteField
from unicef_restlib.serializers import (
    DeletableSerializerMixin,
    PKSerializerMixin,
    WritableNestedChildSerializerMixin,
    WritableNestedParentSerializerMixin,
)


class ActivitySerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Activity
        fields = ("id", "activity_type", "activity_count",)


class ImageSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Image
        fields = ("id", "filename",)


class ReviewSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Review
        fields = ("id", "user", "rating",)


class BookSerializer(
        DeletableSerializerMixin,
        WritableNestedChildSerializerMixin,
        serializers.ModelSerializer
):
    class Meta(DeletableSerializerMixin.Meta, WritableNestedChildSerializerMixin.Meta):
        model = Book
        fields = ("id", "name", "sku_number", "author",)


class AuthorSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    books = BookSerializer(many=True, required=False)
    activities = ActivitySerializer(many=True, required=False)
    profile_images = ImageSerializer(many=True, required=False)
    full_images = ImageSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, required=False)

    class Meta:
        model = Author
        fields = "__all__"


class AuthorPKSerializer(PKSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("pk", "first_name", "last_name",)


class AuthorIDSerializer(PKSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name",)


class ISBNSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = ISBN
        fields = ("code",)


class BookISBNSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    isbn = ISBNSerializer(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = ("name", "isbn", "author",)


class BookForwardSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Book
        fields = ("id", "name",)


class ISBNForwardSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    book = BookForwardSerializer()

    class Meta:
        model = ISBN
        fields = ("id", "code", "book",)


class AuthorSeparatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name",)


class BookSeparatedSerializer(serializers.ModelSerializer):
    author = SeparatedReadWriteField(
        read_field=AuthorSeparatedSerializer(read_only=True)
    )

    class Meta:
        model = Book
        fields = ("id", "author", "name", "sku_number",)
