import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_view(client, book, author):
    response = client.get(reverse("sample:book-list"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk

    response = client.get("{}?auditor__pk={}".format(
        reverse("sample:book-list"),
        author.pk
    ))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == book.pk
