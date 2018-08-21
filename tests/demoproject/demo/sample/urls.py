from demo.sample import views
from django.conf.urls import include, url
from rest_framework import routers

from unicef_restlib.routers import NestedComplexRouter

app_name = 'sample'

router = routers.SimpleRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(
    r'authors-safe',
    views.AuthorSafeTenantViewSet,
    base_name='author-safe',
)
router.register(r'books', views.BookViewSet)
router.register(
    r'book-filter-nested',
    views.BookFilterNestedViewSet,
    base_name="book-filter-nested",
)
router.register(
    r'book-nested/(?P<author_pk>\d+)/',
    views.BookNestedViewSet,
    base_name="book-nested",
)
router.register(
    r'book-root-nested/(?P<author_pk>\d+)/',
    views.BookRootNestedViewSet,
    base_name="book-root-nested",
)

nested = NestedComplexRouter(router, r'authors', lookup='author')
nested.register(r'books', views.BookViewSet, base_name='author-books')

urlpatterns = [
    url(
        r'^authors/paginate/$',
        views.AuthorPaginateView.as_view(),
        name='authors-paginate'
    ),
    url(
        r'^authors/meta/cru/$',
        views.AuthorMetaCRUView.as_view(),
        name='authors-meta-cru'
    ),
    url(
        r'^authors/meta/fsm/$',
        views.AuthorMetaFSMListView.as_view(),
        name='authors-meta-fsm-list'
    ),
    url(
        r'^authors/meta/fsm/(?P<pk>\d+)/$',
        views.AuthorMetaFSMView.as_view(),
        name='authors-meta-fsm'
    ),
    url(
        r'^reviews/meta/fsm/(?P<pk>\d+)/$',
        views.ReviewMetaFSMView.as_view(),
        name='review-meta-fsm'
    ),
    url(r'^list', view=views.AuthorView.as_view(), name='list'),
    url(r'^', include(nested.urls)),
    url(r'^', include(router.urls)),
]
