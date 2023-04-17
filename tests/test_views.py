from django.db import ProgrammingError
from django.urls import reverse

import pytest

from demo.sample.models import Book
from demo.sample.utils import author_description

pytestmark = pytest.mark.django_db


def test_view_get(client, book):
    response = client.get(reverse("sample:book-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk
    assert data[0]["author_description"] == author_description(book.author)


def test_view_get_no_parent(client, author):
    response = client.get(reverse("sample:author-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == author.pk


def test_view_filter(client, book, author):
    assert author.active
    response = client.get(
        "{}?auditor__pk={}".format(
            reverse("sample:book-filter-nested-list"),
            author.pk,
        )
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk


def test_view_filter_true(client, book, author):
    assert author.active
    response = client.get(
        "{}?active=true".format(
            reverse("sample:book-filter-nested-list"),
        )
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_view_filter_invalid(client, book, author):
    author.active = False
    author.save()
    assert not author.active
    response = client.get(
        "{}?auditor__pk={}".format(
            reverse("sample:book-filter-nested-list"),
            author.pk,
        )
    )
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


def test_view_filter_isnull(client, book, author, superuser):
    client.force_login(superuser)
    assert author.first_name
    response = client.get(
        "{}?first_name_exists=true".format(
            reverse("sample:list"),
        )
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    # get opposite
    response = client.get(
        "{}?first_name_exists=false".format(
            reverse("sample:list"),
        )
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_safe_tenant(client, author):
    response = client.get(reverse("sample:author-safe-list"))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_safe_tenant_error(client, superuser):
    client.force_login(superuser)
    with pytest.raises(ProgrammingError):
        client.get(reverse("sample:author-safe-error-list"))


def test_nested_view_get_parent_object_none(client, author):
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


def test_nested_view_get_root_object_no_parent(client, author):
    book_qs = Book.objects
    book_count = book_qs.count()
    response = client.post(
        reverse("sample:book-no-parent-nested-list", args=[author.pk]),
        data={
            "name": "Scary Tales",
            "sku_number": "123",
            "genre": "scifi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Scary Tales"
    assert data["author"] is None
    assert book_qs.count() == book_count + 1


@pytest.mark.parametrize(
    "query_string, results_len ",
    [
        ("", 3),
        ("?first_name=demo", 1),
        ("?search=de", 1),
        ("?first_name=test,demo", 2),
        ("?name=test", 2),
        ("?custom=best", 2),
    ],
)
def test_query_string_api_view(api_client, superuser, query_string, results_len, authors):
    authors.get(first_name="demo", last_name="test", active=False)
    authors.get(first_name="test", last_name="demo")
    authors.get(first_name="rambo")

    api_client.force_authenticate(user=superuser)

    url = reverse("sample:list") + query_string
    results = api_client.get(url, format="json").json()

    assert len(results) == results_len


def test_nested_url(client, author, book):
    url = "{}{}/books/".format(reverse("sample:author-list"), author.pk)
    response = client.get(url)
    assert response.status_code == 200
