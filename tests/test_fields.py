from collections import OrderedDict

import pytest
from demo.sample.serializers import BookSeparatedSerializer, BookSeparatedWriteSerializer, BookSerializer
from django.forms.models import model_to_dict

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
        "author": OrderedDict(model_to_dict(author))
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
    assert field1._kwargs == field2._kwargs
