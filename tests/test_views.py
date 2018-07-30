import pytest
from django.urls import reverse

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
        reverse("sample:book-list"),
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
        reverse("sample:book-list"),
        author.pk,
    ))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
