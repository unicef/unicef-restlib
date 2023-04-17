from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

import pytest
from unittest.mock import Mock

from demo.sample.models import Activity, Author, Book, Category, Image, ISBN, Review
from demo.sample.serializers import (
    AuthorIDSerializer,
    AuthorPKSerializer,
    AuthorReviewsSerializer,
    AuthorSerializer,
    BookISBNSerializer,
    CategoryAbstractPKSerializer,
    CategoryMissingPKSerializer,
    CategorySerializer,
    ISBNForwardSerializer,
    ReviewAuthorSerializer,
    ReviewUserSerializer,
)

pytestmark = pytest.mark.django_db


def test_one_to_one_create(author):
    serializer = BookISBNSerializer(
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "author": author.pk,
            "isbn": {
                "code": "54321",
            },
        }
    )
    serializer.is_valid(raise_exception=True)
    book = serializer.save()
    assert ISBN.objects.filter(book=book, code="54321").exists()


def test_one_to_one_update(author, book, isbn):
    assert book.name != "Scary Tales"
    assert isbn.code != "54321"
    serializer = BookISBNSerializer(
        book,
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "author": author.pk,
            "isbn": {
                "code": "54321",
            },
        },
    )

    serializer.is_valid(raise_exception=True)
    book_updated = serializer.save()
    assert book_updated.name == "Scary Tales"
    isbn_updated = ISBN.objects.get(pk=isbn.pk)
    assert isbn_updated.code == "54321"


def test_one_to_one_partial_update(book, isbn):
    assert isbn.code != "54321"
    serializer = BookISBNSerializer(
        book,
        partial=True,
        data={
            "isbn": {
                "code": "54321",
            }
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()
    isbn_updated = ISBN.objects.get(pk=isbn.pk)
    assert isbn_updated.code == "54321"


def test_one_to_one_create_through_update(book):
    isbn_qs = ISBN.objects.filter(book=book, code="54321")
    assert not isbn_qs.exists()
    serializer = BookISBNSerializer(
        book,
        partial=True,
        data={
            "isbn": {
                "code": "54321",
            }
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert isbn_qs.exists()


def test_one_to_one_create_through_update_required(book):
    serializer = BookISBNSerializer(
        book,
        partial=True,
        data={
            "isbn": {
                "wrong": "54321",
            }
        },
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert err.value.detail == {"isbn": {"code": ["This field is required."]}}


def test_one_to_one_nullable(book, isbn):
    isbn_qs = ISBN.objects.filter(book=book)
    assert isbn_qs.exists()
    serializer = BookISBNSerializer(
        book,
        partial=True,
        data={
            "isbn": None,
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert not isbn_qs.exists()


def test_many_create():
    assert Book.objects.count() == 0
    author_qs = Author.objects.filter(first_name="Joe")
    assert not author_qs.exists()
    serializer = AuthorSerializer(
        data={
            "first_name": "Joe",
            "last_name": "Soap",
            "books": [{"name": "Scary Tales 1", "sku_number": "123"}, {"name": "Scary Tales 2", "sku_number": "321"}],
        }
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert author_qs.exists()


def test_many_update(author, books):
    book_1 = books.get()
    book_2 = books.get()
    assert author.first_name != "Changed"
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 2
    book_1_name = "New Scary Tales 1"
    book_2_name = "New Scary Tales 2"
    assert book_1.name != book_1_name
    assert book_2.name != book_2_name
    serializer = AuthorSerializer(
        author,
        data={
            "first_name": "Changed",
            "last_name": "Soap",
            "books": [
                {"id": book_1.pk, "name": book_1_name, "sku_number": "123"},
                {"id": book_2.pk, "name": book_2_name, "sku_number": "321"},
            ],
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    author_updated = Author.objects.get(pk=author.pk)
    assert author_updated.first_name == "Changed"
    assert book_qs.count() == 2
    book_1_updated = Book.objects.get(pk=book_1.pk)
    assert book_1_updated.name == book_1_name
    book_2_updated = Book.objects.get(pk=book_2.pk)
    assert book_2_updated.name == book_2_name


def test_many_partial_update(author, books):
    book_1 = books.get()
    book_2 = books.get()
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 2
    book_1_name = "New Scary Tales 1"
    assert book_1.name != book_1_name
    serializer = AuthorSerializer(author, partial=True, data={"books": [{"id": book_1.pk, "name": book_1_name}]})

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 2
    book_1_updated = Book.objects.get(pk=book_1.pk)
    assert book_1_updated.name == book_1_name
    book_2_updated = Book.objects.get(pk=book_2.pk)
    assert book_2_updated.name == book_2.name


def test_many_create_through_update(author):
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 0
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"name": "Book 1", "sku_number": "123"},
                {"name": "Book 2", "sku_number": "321"},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 2
    assert Book.objects.filter(author=author, name="Book 1").exists()
    assert Book.objects.filter(author=author, name="Book 2").exists()


def test_many_update_mix(author, books):
    book_1 = books.get(author=author)
    book_2 = books.get(author=author)
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 2
    serializer = AuthorSerializer(
        author,
        data={
            "first_name": "Joe",
            "last_name": "Soap",
            "books": [
                {"id": book_1.pk, "name": "Scary Tales 1", "sku_number": "123"},
                {"id": book_2.pk, "name": "Scary Tales 2", "sku_number": "456"},
                {"name": "Scary Tales 3", "sku_number": "789"},
            ],
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 3
    assert list(book_qs.values_list("name", flat=True)) == [
        "Scary Tales 1",
        "Scary Tales 2",
        "Scary Tales 3",
    ]


def test_many_partial_update_mix(author, book):
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 1
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"id": book.pk, "name": "Scary Tales 1", "sku_number": "123"},
                {"name": "Scary Tales 2", "sku_number": "456"},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 2
    assert list(book_qs.values_list("name", flat=True)) == [
        "Scary Tales 1",
        "Scary Tales 2",
    ]


def test_many_deleting_excess(author, books):
    book_1 = books.get(author=author)
    books.get(author=author)
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 2
    serializer = AuthorSerializer(
        author,
        data={
            "first_name": "Joe",
            "last_name": "Soap",
            "books": [
                {"id": book_1.pk, "name": "Scary Tales 1", "sku_number": "123"},
                {"name": "Scary Tales 3", "sku_number": "789"},
            ],
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 2
    assert list(book_qs.values_list("name", flat=True)) == [
        "Scary Tales 1",
        "Scary Tales 3",
    ]


def test_many_missed(author):
    book_qs = Book.objects.filter(author=author)
    assert not book_qs.exists()
    serializer = AuthorSerializer(
        author, partial=True, data={"books": [{"id": 404, "name": "Scary Tales", "sku_number": "123"}]}
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert err.value.detail == {"books": [{"id": ["Book with pk `404` doesn't exists."]}]}
    assert not book_qs.exists()


def test_many_duplication(author, book):
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 1
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"id": book.pk, "name": "Scary Tales", "sku_number": "123"},
                {"id": book.pk, "name": "Scary Tales", "sku_number": "123"},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

        assert {"books": [{}, {"id": ["Duplication book with pk `{}`.".format(book.pk)]}]} == err.value.detail
    assert book_qs.count() == 1


def test_many_nesting_raises(author, books):
    book_1 = books.get(author=author)
    book_2 = books.get(author=author)
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"id": book_1.pk, "name": "Scary Tales", "sku_number": "123"},
                {"id": book_2.pk, "name": "Scary Tales", "sku_number": "123"},
            ]
        },
    )
    serializer.fields["books"].child.update = Mock(
        side_effect=serializers.ValidationError({"non_field_error": ["Some error."]})
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert {"books": [{"non_field_error": ["Some error."]}, {"non_field_error": ["Some error."]}]} == err.value.detail


def test_forward_create():
    isbn_qs = ISBN.objects.filter(code="54321")
    assert not isbn_qs.exists()
    serializer = ISBNForwardSerializer(
        data={
            "code": "54321",
            "book": {
                "name": "Scary Tales",
                "sku_number": "123",
            },
        }
    )

    serializer.is_valid(raise_exception=True)
    isbn = serializer.save()

    assert isbn_qs.exists()
    assert isbn.book.name == "Scary Tales"


def test_forward_update(isbn):
    book_name = "Scary Tales"
    assert isbn.book.name != book_name
    serializer = ISBNForwardSerializer(
        isbn,
        data={
            "code": "54321",
            "book": {
                "name": book_name,
                "sku_number": "123",
            },
        },
    )

    serializer.is_valid(raise_exception=True)
    isbn = serializer.save()

    assert isbn.book.name == book_name
    book = Book.objects.get(pk=isbn.book.pk)
    assert book.name == book_name


def test_generic_create():
    serializer = AuthorSerializer(
        data={
            "first_name": "Joe",
            "last_name": "Soap",
            "activities": [
                {"activity_type": "view", "activity_count": 10},
                {"activity_type": "read", "activity_count": 15},
            ],
        }
    )

    serializer.is_valid(raise_exception=True)
    author = serializer.save()

    author_content_type = ContentType.objects.get_for_model(Author)
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type="view",
        activity_count=10,
    ).exists()
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type="read",
        activity_count=15,
    ).exists()


def test_generic_update(author, activities):
    activity_1 = activities.get()
    activity_2 = activities.get()
    activity_1_type = "".join([activity_1.activity_type, "view"])
    activity_2_type = "".join([activity_2.activity_type, "read"])
    assert activity_1.activity_type != activity_1_type
    assert activity_2.activity_type != activity_2_type
    serializer = AuthorSerializer(
        author,
        data={
            "first_name": "Changed",
            "last_name": "Soap",
            "activities": [
                {
                    "id": activity_1.pk,
                    "activity_type": activity_1_type,
                    "activity_count": 10,
                },
                {
                    "id": activity_2.pk,
                    "activity_type": activity_2_type,
                    "activity_count": 15,
                },
            ],
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    author_content_type = ContentType.objects.get_for_model(Author)
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type=activity_1_type,
        activity_count=10,
    ).exists()
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type=activity_2_type,
        activity_count=15,
    ).exists()


def test_generic_create_through_update(author):
    author_content_type = ContentType.objects.get_for_model(Author)
    activity_qs = Activity.objects.filter(content_type=author_content_type, object_id=author.pk)
    assert not activity_qs.exists()

    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "activities": [
                {"activity_type": "view", "activity_count": 10},
                {"activity_type": "read", "activity_count": 15},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert activity_qs.count() == 2
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type="view",
        activity_count=10,
    ).exists()
    assert Activity.objects.filter(
        content_type=author_content_type,
        object_id=author.pk,
        activity_type="read",
        activity_count=15,
    ).exists()


def test_coded_generic_representation(author, images):
    image_profile = images.get(author=author, code="author_profile_image")
    image_full = images.get(author=author, code="author_full_image")
    serializer = AuthorSerializer(author)
    assert serializer.data["profile_images"] == [{"id": image_profile.pk, "filename": image_profile.filename}]
    assert serializer.data["full_images"] == [{"id": image_full.pk, "filename": image_full.filename}]


def test_coded_generic_create():
    serializer = AuthorSerializer(
        data={
            "first_name": "Joe",
            "last_name": "Soap",
            "profile_images": [{"filename": "profile_1.png"}, {"filename": "profile_2.png"}],
            "full_images": [{"filename": "full_1.png"}],
        }
    )

    serializer.is_valid(raise_exception=True)
    author = serializer.save()

    author_content_type = ContentType.objects.get_for_model(Author)
    assert list(
        Image.objects.filter(
            content_type=author_content_type, object_id=author.pk, code="author_profile_image"
        ).values_list("filename", flat=True)
    ) == ["profile_1.png", "profile_2.png"]
    assert list(
        Image.objects.filter(
            content_type=author_content_type, object_id=author.pk, code="author_full_image"
        ).values_list("filename", flat=True)
    ) == ["full_1.png"]


def test_unique(author, book):
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 1
    serializer = AuthorSerializer(
        author, partial=True, data={"books": [{"name": "Scary Tales", "sku_number": book.sku_number}]}
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()
    assert err.value.detail == {"books": [{"sku_number": ["book with this sku number already exists."]}]}
    assert book_qs.count() == 1


def test_unique_for_new(author):
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"name": "Scary Tales 1", "sku_number": "123"},
                {"name": "Scary Tales 2", "sku_number": "123"},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert err.value.detail == {"books": [{}, {"sku_number": ["book with this sku number already exists."]}]}
    assert not Book.objects.filter(author=author).exists()


# TODO: Fix this.
@pytest.mark.skip("Unique together validation is not working.")
def test_unique_together(author, user):
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "reviews": [
                {"user": user.pk, "rating": 3},
                {"user": user.pk, "rating": 5},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert err.value.detail == {"reviews": [{"non_field_error": ["This fields author, user must make a unique set."]}]}
    assert not Review.objects.filter(author=author).exists()


def test_deleting(author, books):
    book_1 = books.get(author=author)
    book_2 = books.get(author=author)
    book_qs = Book.objects.filter(author=author)
    assert book_qs.count() == 2
    serializer = AuthorSerializer(
        author,
        partial=True,
        data={
            "books": [
                {"id": book_1.pk, "_delete": True},
                {"id": book_2.pk, "name": "Scary Tales 2", "sku_number": "123"},
            ]
        },
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert book_qs.count() == 1
    assert book_qs.filter(pk=book_2.pk).exists()


def test_deleting_on_create(author):
    serializer = AuthorSerializer(
        author, partial=True, data={"books": [{"name": "Scary Tales", "sku_number": "123", "_delete": True}]}
    )

    serializer.is_valid(raise_exception=True)
    with pytest.raises(serializers.ValidationError) as err:
        serializer.save()

    assert err.value.detail == {"books": [{"_delete": ["You can't delete not exist object."]}]}


# RecursiveListSerializer Tests


def test_recursive_list(categories):
    category = categories.get()
    category_qs = Category.objects.filter(name="New Child", parent=category)
    assert not category_qs.exists()
    serializer = CategorySerializer(category, data={"name": "New Category", "children": [{"name": "New Child"}]})

    assert serializer.is_valid()
    category = serializer.save()

    assert category.name == "New Category"
    assert category_qs.exists()


# PKSerializerMixin Tests


def test_pk_field():
    serializer = AuthorPKSerializer()
    assert serializer.pk_field == serializer.fields["pk"]


def test_id_field():
    serializer = AuthorIDSerializer()
    assert serializer.pk_field == serializer.fields["id"]


def test_pk_abstract():
    serializer = CategoryAbstractPKSerializer()
    with pytest.raises(ValueError):
        serializer.pk_field


def test_pk_missing():
    serializer = CategoryMissingPKSerializer()
    with pytest.raises(AssertionError):
        serializer.pk_field


# WritableNestedParentSerializerMixin Tests


def test_writable_nested_many_to_one():
    serializer = ReviewAuthorSerializer(data={"rating": 1, "author": {"first_name": "First", "last_name": "Last"}})
    serializer.is_valid(raise_exception=True)
    with pytest.raises(AssertionError):
        serializer.save()


def test_writable_nested_validation_not_implemented(user):
    serializer = AuthorReviewsSerializer(
        data={"first_name": "First", "last_name": "Last", "reviews": [{"rating": 1, "user": user.pk}]}
    )
    serializer.is_valid()
    with pytest.raises(NotImplementedError):
        serializer.save()


# UserContextSerializerMixin Tests


def test_user_context_from_context_param(user):
    serializer = ReviewUserSerializer(data={"rating": 1}, context={"user": user})
    serializer.get_user() == user


def test_user_context_from_context_request(rf, user):
    request = rf.get("sample:author-list")
    request.user = user
    serializer = ReviewUserSerializer(data={"rating": 1}, context={"request": request})
    serializer.get_user() == user
