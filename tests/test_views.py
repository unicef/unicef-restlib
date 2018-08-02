import pytest
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


@pytest.mark.django_db
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
