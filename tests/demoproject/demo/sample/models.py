from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils import Choices
from unicef_djangolib.fields import CodedGenericRelation


class Activity(models.Model):
    activity_type = models.CharField(max_length=50)
    activity_count = models.IntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    obj = GenericForeignKey()


class Image(models.Model):
    filename = models.CharField(max_length=150)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    obj = GenericForeignKey()
    code = models.CharField(max_length=50, blank=True)


class Author(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    profile_images = CodedGenericRelation(Image, code="author_profile_image")
    full_images = CodedGenericRelation(Image, code="author_full_image")
    activities = GenericRelation(Activity)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Book(models.Model):
    GENRE_CHOICES = Choices(
        ("fantasy", "Fantasy"),
        ("scifi", "Sci-Fi"),
        ("thriller", "Thriller"),
        ("western", "Western"),
    )

    author = models.ForeignKey(
        Author,
        related_name="books",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    sku_number = models.CharField(max_length=20, unique=True)
    genre = models.CharField(max_length=50, blank=True, choices=GENRE_CHOICES)

    def __str__(self):
        return self.name


class ISBN(models.Model):
    book = models.OneToOneField(
        Book,
        related_name="isbn",
        on_delete=models.CASCADE,
    )
    code = models.CharField(max_length=20, unique=True)


class Review(models.Model):
    author = models.ForeignKey(
        Author,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = [["author", "user"]]


class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.CASCADE,
    )
