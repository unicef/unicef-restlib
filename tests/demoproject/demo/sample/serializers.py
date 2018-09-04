from demo.sample.fields import FileTypeModelChoiceField
from demo.sample.models import Activity, Author, Book, Category, CategoryAbstract, FileType, Image, ISBN, Review
from rest_framework import serializers

from unicef_restlib.fields import (
    CommaSeparatedExportField,
    DynamicChoicesField,
    SeparatedReadWriteField,
    WriteListSerializeFriendlyRecursiveField,
)
from unicef_restlib.serializers import (
    DeletableSerializerMixin,
    PKSerializerMixin,
    RecursiveListSerializer,
    UserContextSerializerMixin,
    WritableNestedChildSerializerMixin,
    WritableNestedParentSerializerMixin,
    WritableNestedSerializerMixin,
)


class ActivitySerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Activity
        fields = ("id", "activity_type", "activity_count",)


class ImageFileTypeSerializer(serializers.ModelSerializer):
    file_type = FileTypeModelChoiceField(
        queryset=FileType.objects.filter(code='image')
    )

    class Meta:
        model = Image
        fields = ("file_type",)


class ImageFileTypeChoiceSerializer(serializers.ModelSerializer):
    file_type = serializers.ChoiceField(choices=[(1, "First"), (2, "Second")])

    class Meta:
        model = Image
        fields = ("file_type",)


class ImageSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Image
        fields = ("id", "filename",)


class ReviewSerializer(WritableNestedChildSerializerMixin, serializers.ModelSerializer):
    class Meta(WritableNestedChildSerializerMixin.Meta):
        model = Review
        fields = ("id", "user", "rating",)


class ReviewUserSerializer(UserContextSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "user", "rating",)


class ReviewMetaSerializer(serializers.ModelSerializer):
    rating = DynamicChoicesField(
        choices={1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        required=False,
    )

    class Meta:
        model = Review
        fields = ("id", "user", "rating", "status", "active",)


class BookSerializer(
        DeletableSerializerMixin,
        WritableNestedChildSerializerMixin,
        serializers.ModelSerializer
):
    genre = DynamicChoicesField(choices=Book.GENRE_CHOICES, required=False)

    class Meta(DeletableSerializerMixin.Meta, WritableNestedChildSerializerMixin.Meta):
        model = Book
        fields = ("id", "name", "sku_number", "author", "genre",)


class AuthorSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    books = BookSerializer(many=True, required=False)
    activities = ActivitySerializer(many=True, required=False)
    profile_images = ImageSerializer(many=True, required=False)
    full_images = ImageSerializer(many=True, required=False)
    reviews = ReviewSerializer(many=True, required=False)
    review_ratings = CommaSeparatedExportField(
        source="reviews",
        required=False,
        export_attr="rating"
    )

    class Meta:
        model = Author
        fields = "__all__"


class AuthorMetaSerializer(serializers.ModelSerializer):
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


class ReviewAuthorSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Review
        fields = ("id", "rating", "author")


class AuthorReviewsSerializer(WritableNestedParentSerializerMixin, serializers.ModelSerializer):
    reviews = ReviewMetaSerializer(many=True)

    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "reviews")


class AuthorSeparatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "active",)


class BookSeparatedSerializer(serializers.ModelSerializer):
    author = SeparatedReadWriteField(
        read_field=AuthorSeparatedSerializer(read_only=True),
        label="Author",
    )

    class Meta:
        model = Book
        fields = ("id", "author", "name", "sku_number",)


class BookSeparatedWriteSerializer(serializers.ModelSerializer):
    author = SeparatedReadWriteField(
        read_field=AuthorSeparatedSerializer(read_only=True),
        write_field=AuthorSeparatedSerializer(),
        label="Author",
    )

    class Meta:
        model = Book
        fields = ("id", "author", "name", "sku_number",)


class CategorySerializer(WritableNestedSerializerMixin, serializers.ModelSerializer):
    children = RecursiveListSerializer(
        child=WriteListSerializeFriendlyRecursiveField(required=False),
        required=False
    )

    class Meta(WritableNestedSerializerMixin.Meta):
        model = Category
        fields = ("id", "name", "parent", "children",)


class CategoryAbstractPKSerializer(PKSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CategoryAbstract


class CategoryMissingPKSerializer(PKSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)
