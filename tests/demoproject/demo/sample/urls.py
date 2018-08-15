from demo.sample import views
from django.conf.urls import url
from rest_framework import routers

app_name = 'sample'

router = routers.DefaultRouter()
router.register(r'authors/', views.AuthorViewSet)
router.register(r'books/', views.BookViewSet)

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
]

urlpatterns += router.urls
