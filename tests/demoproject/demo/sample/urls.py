from demo.sample import views
from django.conf.urls import url
from rest_framework import routers

app_name = 'sample'

router = routers.DefaultRouter()
router.register(r'authors/', views.AuthorViewSet)

urlpatterns = [
    url(
        r'^author/normal/$',
        views.AuthorNormalView.as_view(),
        name='author-normal'
    ),
    url(r'^author/$', views.AuthorView.as_view(), name='author-view'),
    url(
        r'^author/transform/$',
        views.AuthorTransformView.as_view(),
        name='author-transform'
    ),
    url(
        r'^author/invalid/$',
        views.AuthorInvalidView.as_view(),
        name='author-invalid'
    ),
    url(
        r'^author/template/$',
        views.AuthorTemplateView.as_view(),
        name='author-template'
    ),
    url(r'^book/$', views.BookView.as_view(), name='book-view'),
]

urlpatterns += router.urls
