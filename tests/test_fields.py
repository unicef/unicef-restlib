from collections import OrderedDict
from unittest.mock import Mock, patch

import pytest
from demo.sample.serializers import (
    AuthorSerializer,
    BookSeparatedSerializer,
    BookSeparatedWriteSerializer,
    BookSerializer,
    ImageFileTypeSerializer,
    ReviewMetaSerializer,
)
from django.forms.models import model_to_dict
from tests.factories import FileTypeFactory

pytestmark = pytest.mark.django_db


def test_representation(author, book):
    serializer = BookSeparatedSerializer(book)

    assert serializer.data == {
        "id": book.pk,
        "name": book.name,
        "sku_number": book.sku_number,
        "author": {
            "id": author.pk,
            "first_name": author.first_name,
            "last_name": author.last_name,
            "active": True,
        }
    }


def test_creation(author):
    serializer = BookSeparatedSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
        "author": author.pk,
    })
    serializer.is_valid(raise_exception=True)
    book = serializer.save()

    assert book.author == author
    assert serializer.data == {
        "id": book.pk,
        "name": "Scary Tales",
        "sku_number": "123",
        "author": OrderedDict(model_to_dict(author)),
    }


def test_validation():
    serializer = BookSeparatedSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
        "author": 404,
    })

    assert not serializer.is_valid()
    assert serializer.errors == {"author": [
        "Invalid pk \"404\" - object does not exist."
    ]}


def test_validate_empty_not_required():
    """Empty value for non-required field, still passes validation"""
    serializer = BookSeparatedSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
    })
    assert serializer.is_valid()


def test_validate_empty_required():
    serializer = BookSeparatedWriteSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
    })
    assert not serializer.is_valid()
    assert serializer.errors == {"author": ["This field is required."]}


def test_validate_empty_required_partial(book):
    serializer = BookSeparatedWriteSerializer(book, partial=True, data={
        "name": "Scary Tales",
        "sku_number": "123",
    })
    assert serializer.is_valid()


def test_validate_none_not_required():
    """None value for non-required field, still passes validation"""
    serializer = BookSeparatedSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
        "author": None
    })
    assert serializer.is_valid()


def test_validate_none_required():
    serializer = BookSeparatedWriteSerializer(data={
        "name": "Scary Tales",
        "sku_number": "123",
        "author": None
    })
    assert not serializer.is_valid()
    assert serializer.errors == {"author": ["This field may not be null."]}


def test_serializers_tree(book):
    serializer = BookSeparatedSerializer(book, context={"var1": 123})

    read_field = serializer.fields["author"].read_field
    write_field = serializer.fields["author"].write_field

    assert read_field.source_attrs == serializer.fields["author"].source_attrs
    assert write_field.source_attrs == serializer.fields["author"].source_attrs
    assert write_field.root == serializer
    assert write_field.context == {"var1": 123}


def test_field_building(book):
    serializer1 = BookSeparatedSerializer(book)
    serializer2 = BookSerializer(book)

    field1 = serializer1.fields["author"].write_field
    field2 = serializer2.fields["author"]
    assert field1.__class__ == field2.__class__
    assert field1._args == field2._args
    assert not field1._kwargs == field2._kwargs
    assert "label" in field1._kwargs
    assert "label" not in field2._kwargs


def test_comma_separated_export_field(author, reviews):
    reviews.get(author=author, rating=1)
    reviews.get(author=author, rating=2)
    serializer = AuthorSerializer(author)
    data = serializer.data
    assert data["review_ratings"] == "1, 2"


def test_comma_separated_export_field_skip(author, reviews):
    reviews.get(author=author, rating=1)
    reviews.get(author=author, rating=2)
    mock_smart = Mock(side_effect=KeyError)
    with patch("unicef_restlib.fields.get_attribute_smart", mock_smart):
        serializer = AuthorSerializer(author)
        data = serializer.data
        assert "review_ratings" not in data


def test_comma_separated_export_field_exception(author, reviews):
    reviews.get(author=author, rating=1)
    reviews.get(author=author, rating=2)
    mock_smart = Mock(side_effect=KeyError)
    with patch("unicef_restlib.fields.get_attribute_smart", mock_smart):
        serializer = AuthorSerializer(author)
        serializer.fields["review_ratings"].required = True
        with pytest.raises(KeyError):
            serializer.data


def test_dynamic_choices_field():
    serializer = BookSerializer(data={
        "name": "Scary Tales",
        "genre": "western",
        "sku_number": "123"
    })

    assert serializer.is_valid()
    data = serializer.data
    assert data["genre"] == "Western"


def test_dynamic_choices_field_not_choices(user):
    serializer = ReviewMetaSerializer(data={
        "user": user.pk,
        "rating": 1,
        "status": "new"
    })

    assert serializer.is_valid()
    data = serializer.data
    assert data["rating"] == 1


def test_dynamic_choices_field_invalid():
    serializer = BookSerializer(data={
        "name": "Scary Tales",
        "genre": "wrong",
        "sku_number": "123"
    })

    assert not serializer.is_valid()
    assert serializer.errors == {"genre": ["\"wrong\" is not a valid choice."]}


def test_model_choice_field_valid_serializer():
    file_type = FileTypeFactory(code="image")
    valid_serializer = ImageFileTypeSerializer(
        data={'file_type': file_type.pk}
    )
    assert valid_serializer.is_valid()


def test_model_choice_field_invalid_serializer():
    file_type = FileTypeFactory(code="wrong")
    invalid_serializer = ImageFileTypeSerializer(
        data={'file_type': file_type.pk}
    )
    assert not invalid_serializer.is_valid()
    assert 'file_type' in invalid_serializer.errors
    s = 'Invalid option "{pk_value}" - option is not available.'.format(
        pk_value=file_type.pk
    )
    assert s in invalid_serializer.errors['file_type']
