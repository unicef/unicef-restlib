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
]

urlpatterns += router.urls
