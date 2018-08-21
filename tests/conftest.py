import pytest
from rest_framework.test import APIClient
from tests import factories


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return factories.UserFactory()


@pytest.fixture
def superuser():
    return factories.UserFactory(
        username="superusername",
        email="super@example.com",
        is_superuser=True,
    )


@pytest.fixture
def author():
    return factories.AuthorFactory()


@pytest.fixture
def authors():
    class AuthorFactory:
        def get(self, first_name=None):
            kwargs = {"first_name": first_name} if first_name else {}
            return factories.AuthorFactory(**kwargs)
    return AuthorFactory()


@pytest.fixture
def book(author):
    return factories.BookFactory(author=author)


@pytest.fixture
def books(author):
    class BookFactory:
        def get(self, author=author):
            return factories.BookFactory(author=author)
    return BookFactory()


@pytest.fixture
def isbn(book):
    return factories.ISBNFactory(book=book)


@pytest.fixture
def activity(author):
    return factories.ActivityFactory(author=author)


@pytest.fixture
def activities(author):
    class ActivityFactory:
        def get(self):
            return factories.ActivityFactory(obj=author)
    return ActivityFactory()


@pytest.fixture
def file_type():
    return factories.FileTypeFactory()


@pytest.fixture
def image(author):
    return factories.ImageFactory(obj=author)


@pytest.fixture
def images(author):
    class ImageFactory:
        def get(self, author=author, **kwargs):
            return factories.ImageFactory(obj=author, **kwargs)
    return ImageFactory()


@pytest.fixture
def review(author, user):
    return factories.ReviewFactory(author=author, user=user)


@pytest.fixture
def reviews(author, user):
    class ReviewFactory:
        def get(self, **kwargs):
            return factories.ReviewFactory(**kwargs)
    return ReviewFactory()


@pytest.fixture
def category():
    return factories.CategoryFactory()


@pytest.fixture
def categories():
    class CategoryFactory:
        def get(self, **kwargs):
            return factories.CategoryFactory(**kwargs)
    return CategoryFactory()
