from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    path("product/", include("products.urls")),
    # path('add_comment_to_post/<int:id>/',views.add_comment_to_post),
]
