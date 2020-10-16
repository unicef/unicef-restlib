from django.conf.urls import include, url
from rest_framework import routers

from unicef_restlib.routers import NestedComplexRouter

from demo.sample import views

app_name = 'sample'

router = routers.SimpleRouter()
router.register(r'authors', views.AuthorViewSet)
router.register(
    r'authors-safe',
    views.AuthorSafeTenantViewSet,
    basename='author-safe',
)
router.register(
    r'authors-safe-error',
    views.AuthorSafeTenantErrorViewSet,
    basename='author-safe-error',
)
router.register(
    r'authors-cru',
    views.AuthorMetaCRUViewSet,
    basename='author-cru',
)
router.register(r'books', views.BookViewSet)
router.register(
    r'book-filter-nested',
    views.BookFilterNestedViewSet,
    basename="book-filter-nested",
)
router.register(
    r'book-nested/(?P<author_pk>\d+)/',
    views.BookNestedViewSet,
    basename="book-nested",
)
router.register(
    r'book-root-nested/(?P<author_pk>\d+)/',
    views.BookRootNestedViewSet,
    basename="book-root-nested",
)
router.register(
    r'book-no-parent-nested/(?P<author_pk>\d+)/',
    views.BookNoParentNestedViewSet,
    basename="book-no-parent-nested",
)

nested = NestedComplexRouter(router, r'authors', lookup='author')
nested.register(r'books', views.BookViewSet, basename='author-books')

urlpatterns = [
    url(
        r'^authors/paginate/$',
        views.AuthorPaginateView.as_view(),
        name='authors-paginate'
    ),
    url(
        r'^authors/meta/cru/$',
        views.AuthorMetaCRUListView.as_view(),
        name='authors-meta-cru-list'
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
