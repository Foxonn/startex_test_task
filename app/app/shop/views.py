from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test

from rest_framework.generics import (CreateAPIView,
                                     UpdateAPIView)

from .serializers import (UserRegistrationSerializer,
                          OrderSerializer,
                          FileGoodsUploadSerializer)

from rest_framework import status

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.shortcuts import get_object_or_404

from .services import upload_vendor_products
from .models import UploadGoods


def check_admin(user):
    return user.is_superuser


class UserRegistrationViews(CreateAPIView):
    """Регистрация пользователя"""

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class ProductAddToCartViews(CreateAPIView):
    """Добавление товара в корзину"""

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


class FileUploadViews(CreateAPIView):
    """Загрузка файла с товарами от поставщика"""

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FileGoodsUploadSerializer

    def pre_save(self, obj):
        obj.file = self.request.FILES.get('file')


@user_passes_test(check_admin)
@require_http_methods(["GET"])
def products_upload_views(request, filename):
    try:
        qs = get_object_or_404(UploadGoods, file__endswith=filename)

        upload_vendor_products(qs.file.path)
        qs.status = True
        qs.save()

        return JsonResponse(status=status.HTTP_200_OK, data={'detail': True})
    except Exception as err:
        return JsonResponse(
            data={'detail': ascii(err)},
            status=status.HTTP_400_BAD_REQUEST
        )
