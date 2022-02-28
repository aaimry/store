from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

CATEGORY_CHOICES = [('other', 'Разное'), ('fruits', 'Фрукты'), ('vegetables', 'Овощи'), ('beverage', 'Напитки'),
                    ('bakery', 'Выпечка')]


class Products(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    description = models.TextField(max_length=2000, null=True, blank=True, verbose_name='Описание')
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=15, default='other', verbose_name='Категория')
    residue = models.IntegerField(null=False, verbose_name='Остаток')
    price = models.DecimalField(max_digits=9, decimal_places=2, null=False, verbose_name='Цена')

    def get_absolute_url(self):
        return reverse('store:product_check', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title} {self.description} {self.category} {self.residue} {self.price}'

    class Meta:
        db_table = 'Products'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class Basket(models.Model):
    product = models.ForeignKey('store.Products', on_delete=models.CASCADE, related_name='product',
                                verbose_name='Продукт')
    quantity = models.IntegerField(null=False, default=0, verbose_name='Колличество')

    def __str__(self):
        return f'{self.product} {self.quantity}'

    class Meta:
        db_table = 'Basket'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def get_sum(self):
        return self.product.price * self.quantity


class ProductBasket(models.Model):
    product = models.ForeignKey('store.Products', on_delete=models.CASCADE, related_name='product_order',
                                verbose_name='Продукт')
    order = models.ForeignKey('store.Order', on_delete=models.PROTECT, related_name='order_product',
                              verbose_name='Корзина')
    quantity = models.PositiveIntegerField(null=False, default=0, verbose_name='Колличество')

    def get_sum(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product} {self.order} {self.quantity}'

    class Meta:
        db_table = 'ProductBasket'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Order(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='order')
    client_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Имя клиента')
    phone = models.CharField(max_length=100, null=False, blank=False, verbose_name='Телефон')
    address = models.CharField(max_length=100, null=False, blank=False, verbose_name='Адрес')
    datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')

    def __str__(self):
        return f' {self.client_name} {self.phone} {self.address} {self.datetime}'

    def get_total(self):
        total = 0
        ordered_products = ProductBasket.objects.filter(order=self)
        for ordered_product in ordered_products:
            total += ordered_product.get_sum()
        return total

    class Meta:
        db_table = 'Order'
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'
