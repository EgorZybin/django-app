from django.contrib.auth.models import User
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename
    )


def product_image_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename
    )


class Product(models.Model):
    """
    Модель Product представляет товар
    который можно продавать в интернет-магазине.

    Заказы тут: :model:`shopapp.Order`
    """
    class Meta:
        ordering = ['name', 'price']
        # db_table = 'products'
        # verbose_name = 'products
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=100, verbose_name=_('название'), db_index=True)
    description = models.TextField(null=False, blank=True, verbose_name=_('описание'), db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('цена'))
    count = models.IntegerField(verbose_name=_('количество'))
    discount = models.SmallIntegerField(default=0, verbose_name=_('скидка'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('дата создания'))
    archived = models.BooleanField(default=False, verbose_name=_('архивировано'))
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="products", verbose_name=_('создал'))
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path, verbose_name=_('превью'))

    def __str__(self) -> CharField:
        return self.name

    def get_absolute_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_image_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    delivery_address = models.TextField(null=True, blank=True, verbose_name=_('адрес'))
    promocode = models.CharField(max_length=20, null=False, blank=True, verbose_name=_('промокод'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('дата создания'))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders", verbose_name=_('пользователь'))
    products = models.ManyToManyField(Product, related_name="orders", verbose_name=_('товары'))
    receipt = models.FileField(null=True, upload_to="orders/receipts/", verbose_name=_('рецепт'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self) -> str:
        return f"Order(pk={self.pk}, delivery_address={self.delivery_address!r})"
