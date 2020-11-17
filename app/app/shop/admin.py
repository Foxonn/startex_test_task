from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.html import mark_safe
from django.urls import reverse_lazy

from shop.models import Cart, Product, AdvanceUser, Role, Order, UploadGoods


@admin.register(AdvanceUser)
class AdvanceUserAdmin(UserAdmin):
    list_editable = ['is_staff', 'role']
    list_display = [*UserAdmin.list_display, 'role']
    list_per_page = 30
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields':
            (
                'first_name',
                'last_name',
                'middle_name',
                'email',
                'delivery_address',
                'role',
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class OrderAdminInline(admin.TabularInline):
    model = Order
    readonly_fields = ['product', 'total_sum']
    fieldsets = (
        ('Orders', {'fields': ['product', 'count', 'total_sum', ]}),
    )

    def get_queryset(self, request):
        qs = super(OrderAdminInline, self).get_queryset(request)
        if not request.user.is_client:
            return qs
        return qs.filter(cart__pk=request.user.cart.id)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'total_sum']
    inlines = [OrderAdminInline, ]

    fieldsets = (
        ('Cart', {'fields': ['user']}),
        ('Total', {'fields': ['total_sum']}),
    )

    def get_queryset(self, request):
        qs = super(CartAdmin, self).get_queryset(request)
        if not request.user.is_client:
            return qs
        return qs.filter(user=request.user)

    class Meta:
        fields = '__all__'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ('name', 'sku')
    list_display = ['name', 'sku', 'purchase_price', 'retail_price']
    list_editable = ('purchase_price', 'retail_price')
    list_per_page = 30

    class Meta:
        fields = '__all__'


@admin.register(UploadGoods)
class UploadGoodsAdmin(admin.ModelAdmin):
    search_fields = ('file', 'status')
    list_display = ['file_name', 'run_uploads_products_to_db', 'status']
    readonly_fields = ['status']
    fields = [('file', 'status')]

    @staticmethod
    def run_uploads_products_to_db(instance):
        title = "Запустить загрузку товаров поставщика в БД"
        lint_tpl = """
        <a href="{link}" class="link" title="{title}" target="_blank">
            run
        </a>
        """

        link = lint_tpl.format(
            link=reverse_lazy(
                'shop:upload_products', args=[instance.file_name],
            ),
            title=title
        )
        return mark_safe(link)

    class Meta:
        fields = '__all__'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    filter_horizontal = ('permissions',)
    list_display = ['name']
    list_filter = ['name']
    fieldsets = (
        ('Role', {'fields': (
            'name',
            'permissions',
        )}),
    )
