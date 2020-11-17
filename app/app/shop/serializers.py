from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import AdvanceUser, Cart, Product, Order, UploadGoods


class CreateGetCurrentUserCart:
    @staticmethod
    def get_create_cart_for_new_user(user):

        try:
            return get_object_or_404(Cart, user=user)
        except Exception as err:
            return Cart.objects.create(user=user)

    def set_context(self, serializer_field):
        self.user = serializer_field.context['request'].user
        self.cart = self.get_create_cart_for_new_user(self.user)

    def __call__(self):
        return self.cart

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Регистрация пользователя"""

    password = serializers.CharField(
        required=True,
        min_length=1,
        max_length=30,
        style={
            'input_type': 'password',
        },
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=AdvanceUser.objects.all())]
    )

    first_name = serializers.CharField(
        required=True,
        min_length=1,
        max_length=30,
        trim_whitespace=True,
    )

    last_name = serializers.CharField(
        required=True,
        min_length=1,
        max_length=30,
        trim_whitespace=True,
    )

    middle_name = serializers.CharField(
        required=True,
        min_length=1,
        max_length=30,
        trim_whitespace=True,
    )

    delivery_address = serializers.CharField(
        required=True,
        min_length=5,
        max_length=150,
    )

    def create(self, data):
        data['username'] = data.get('email', None)

        user = AdvanceUser(**data)
        user.set_password(data['password'])
        user.save()

        user.password = '***'

        return user

    class Meta:
        model = AdvanceUser
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'email',
            'password',
            'delivery_address',
        ]


class ProductSerializer(serializers.ModelSerializer):
    """Сериализация товара"""

    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """Сериализация заказа"""

    cart = serializers.HiddenField(default=CreateGetCurrentUserCart())

    class Meta:
        model = Order
        fields = ['product', 'count', 'cart']


class FileGoodsUploadSerializer(serializers.ModelSerializer):
    """Сериализация файла с товарами от постовщика"""

    class Meta:
        model = UploadGoods
        fields = ['file']
