# Generated by Django 4.0.1 on 2022-02-07 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_basket_quantity'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductBasket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0, verbose_name='Колличество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='basket_product', to='store.basket', verbose_name='Корзина')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='product_basket', to='store.products', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'ПродуктКорзина',
                'verbose_name_plural': 'ПродуткыКорзины',
                'db_table': 'ProductBasket',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=100, verbose_name='Имя клиента')),
                ('phone', models.CharField(max_length=100, verbose_name='Телефон')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')),
                ('product', models.ManyToManyField(related_name='order_product', to='store.ProductBasket', verbose_name='Продукт')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'db_table': 'Order',
            },
        ),
    ]
