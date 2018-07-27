from demo.sample import views
from rest_framework import routers

app_name = 'sample'

router = routers.DefaultRouter()
router.register(r'authors/', views.AuthorViewSet)
router.register(r'books/', views.BookViewSet)

# urlpatterns = [
#     url(r'^author/$', views.AuthorView.as_view(), name='author-view'),
#     url(r'^book/$', views.BookView.as_view(), name='book-view'),
# ]

urlpatterns = router.urls
