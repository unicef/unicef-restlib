from django.contrib.auth import get_user_model

import factory
import factory.fuzzy

from demo.sample import models


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = get_user_model()
        django_get_or_create = ("username",)


class AuthorFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = models.Author


class BookFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    author = factory.SubFactory(AuthorFactory)
    sku_number = factory.Faker("pystr")

    class Meta:
        model = models.Book


class ISBNFactory(factory.django.DjangoModelFactory):
    code = factory.Faker("isbn13")
    book = factory.SubFactory(BookFactory)

    class Meta:
        model = models.ISBN


class ActivityFactory(factory.django.DjangoModelFactory):
    obj = factory.SubFactory(AuthorFactory)
    activity_type = factory.Faker("word")
    activity_count = factory.Faker("pyint")

    class Meta:
        model = models.Activity


class FileTypeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    code = factory.Faker("word")

    class Meta:
        model = models.FileType
        django_get_or_create = ("code",)


class ImageFactory(factory.django.DjangoModelFactory):
    filename = factory.Faker("file_name")
    obj = factory.SubFactory(AuthorFactory)
    code = factory.fuzzy.FuzzyChoice(["author_profile_image", "author_full_image"])

    class Meta:
        model = models.Image


class ReviewFactory(factory.django.DjangoModelFactory):
    author = factory.SubFactory(AuthorFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker("pyint")

    class Meta:
        model = models.Review


class CategoryFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")

    class Meta:
        model = models.Category
