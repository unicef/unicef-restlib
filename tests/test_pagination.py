import pytest
from demo.sample.models import Author
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_view_paginate_optional(client, authors):
    for __ in range(20):
        authors.get()
    author_qs = Author.objects
    assert author_qs.count() > 10

    # default
    response = client.get(reverse("sample:authors-paginate"))
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 10
    assert data["count"] == author_qs.count()

    # set page size
    response = client.get(
        "{}?page_size=5".format(reverse("sample:authors-paginate"))
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 5
    assert data["count"] == author_qs.count()

    # set page size to `all`
    response = client.get(
        "{}?page_size=all".format(reverse("sample:authors-paginate"))
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" not in data
    assert len(data) == author_qs.count()
