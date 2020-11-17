from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import MinValueValidator
from django.core.validators import FileExtensionValidator
from django.dispatch import receiver
from django.db.models import Sum

import decimal
import os


class AdvanceUser(AbstractUser):
    middle_name = models.CharField(
        max_length=150,
        blank=True,
    )

    delivery_address = models.CharField(
        max_length=150,
        blank=True,
    )

    role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='user'
    )

    @property
    def is_client(self) -> bool:
        if str(self.role) == 'client':
            return True
        return False


class Role(models.Model):
    ROLES = {
        'm': 'manager',
        'c': 'client',
    }

    ROLE_CHOICES = [(i) for i in ROLES.items()]

    name = models.CharField(
        choices=ROLE_CHOICES,
        max_length=15,
        unique=True,
    )

    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='role',
    )

    def __str__(self):
        return self.ROLES[self.name]


class Product(models.Model):
    name = models.CharField(max_length=70)

    sku = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    purchase_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal(1))]
    )

    retail_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal(1))]
    )

    created = models.DateTimeField(auto_now_add=True)

    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='orders',
        on_delete=models.CASCADE
    )

    cart = models.ForeignKey(
        'Cart',
        related_name='orders',
        on_delete=models.CASCADE
    )

    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    @property
    def total_sum(self):
        return self.count * self.product.retail_price

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    user = models.OneToOneField(
        AdvanceUser,
        on_delete=models.CASCADE,
        related_name='cart'
    )

    def __str__(self):
        return self.user.username

    @property
    def count_products(self):
        return self.orders.aggregate(Sum('count')).get('count__sum', 0)

    @property
    def total_sum(self):
        orders = self.orders.all()
        sum_ = 0

        for order in orders:
            sum_ += order.total_sum

        return sum_

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'


class UploadGoods(models.Model):
    file = models.FileField(
        upload_to='uploads/vendors/products',
        validators=[FileExtensionValidator(['csv'])],
        blank=False
    )

    status = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    @property
    def file_name(self):
        return self.__str__()

    def __str__(self):
        return os.path.basename(self.file.name)


@receiver(models.signals.post_delete, sender=UploadGoods)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    return None
