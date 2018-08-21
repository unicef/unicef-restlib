import pytest
from demo.sample.models import Book
from django.urls import reverse
from rest_framework.test import APIClient
from tests.factories import AuthorFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_view_get(client, book):
    response = client.get(reverse("sample:book-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk


def test_view_get_no_parent(client, author):
    response = client.get(reverse("sample:author-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == author.pk


def test_view_filter(client, book, author):
    assert author.active
    response = client.get("{}?auditor__pk={}".format(
        reverse("sample:book-filter-nested-list"),
        author.pk,
    ))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk


def test_view_filter_invalid(client, book, author):
    author.active = False
    author.save()
    assert not author.active
    response = client.get("{}?auditor__pk={}".format(
        reverse("sample:book-filter-nested-list"),
        author.pk,
    ))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_view_filter_no_parent_filter(client, book, author):
    assert author.active
    response = client.get(
        reverse("sample:book-nested-list", args=[author.pk]),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk
    assert data[0]["author"] == author.pk


def test_view_filter_no_parent_filter_not_found(client, book):
    response = client.get(
        reverse("sample:book-nested-list", args=[404]),
    )
    assert response.status_code == 200
    assert response.json() == []


def test_safe_tenant(client, author):
    response = client.get(reverse("sample:author-safe-list"))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_nested_view_get_parent_object_none(client, author):
    book_qs = Book.objects
    book_count = book_qs.count()
    response = client.post(
        reverse("sample:book-nested-list", args=[404]),
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "genre": "scifi",
        },
    )
    assert response.status_code == 404


def test_nested_view_get_parent_object(client, author):
    book_qs = Book.objects
    book_count = book_qs.count()
    response = client.post(
        reverse("sample:book-nested-list", args=[author.pk]),
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "genre": "scifi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Scary Tales"
    assert data["author"] == author.pk
    assert book_qs.count() == book_count + 1


def test_nested_view_get_root_object(client, author):
    book_qs = Book.objects
    book_count = book_qs.count()
    response = client.post(
        reverse("sample:book-root-nested-list", args=[author.pk]),
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "genre": "scifi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Scary Tales"
    assert data["author"] == author.pk
    assert book_qs.count() == book_count + 1


@pytest.mark.parametrize("query_string, results_len ", [('', 2), ('?first_name=demo', 1), ('?search=de', 1)])
def test_query_string_api_view(query_string, results_len):
    user = UserFactory(is_superuser=True)
    AuthorFactory(first_name='demo')
    AuthorFactory(first_name='test')

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse('sample:list') + query_string
    results = client.get(url, format='json').json()

    assert len(results) == results_len


def test_nested_url(client, author, book):
    url = "{}{}/books/".format(reverse("sample:author-list"), author.pk)
    response = client.get(url)
    assert response.status_code == 200
