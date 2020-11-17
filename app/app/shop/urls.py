from django.urls import path, re_path
from . import views

app_name = 'shop'

urlpatterns = [
    path(
        'registration/',
        views.UserRegistrationViews.as_view(),
        name='registration'
    ),
    path(
        'cart/add/',
        views.ProductAddToCartViews.as_view(),
        name='add'
    ),
    re_path(
        '^upload_products/(?P<filename>[^/]+)$',
        views.products_upload_views,
        name='upload_products'
    ),
    path(
        'upload_file/',
        views.FileUploadViews.as_view(),
        name='upload_file'
    ),
]
