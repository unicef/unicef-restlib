from collections import OrderedDict

import pytest
from demo.sample.serializers import BookSeparatedSerializer, BookSerializer
from django.forms.models import model_to_dict

pytestmark = pytest.mark.django_db


class SeparateReadWriteTestCase:
    @classmethod
    def setUpTestData(cls):
        # We disable synchronisation of test models. So we need to create it manually.
        with connection.schema_editor() as editor:
            editor.create_model(Parent)
            editor.create_model(Child1)
            editor.create_model(Child4)

        cls.parent, _ = Parent.objects.get_or_create(id=1, field=1)
        cls.child1, _ = Child1.objects.get_or_create(
            field=2,
            parent=cls.parent
        )
        cls.child4, _ = Child4.objects.get_or_create(
            field=2,
            parent=cls.parent
        )

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

    assert serializer.is_valid() is False
    assert serializer.errors == {"author": [
        "Invalid pk \"404\" - object does not exist."
    ]}


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
