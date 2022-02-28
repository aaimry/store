from django.contrib import admin

from store.models import Products, Basket, Order


class ProductsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'price']
    list_filter = ['title', 'category']
    search_fields = ['title', 'category']
    fields = ['title', 'description', 'category', 'residue', 'price']


admin.site.register(Products, ProductsAdmin)


class BasketAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity']
    list_filter = ['product']
    search_fields = ['product']
    fields = ['product', 'quantity']


admin.site.register(Basket, BasketAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'phone', 'address', 'datetime']
    list_filter = ['datetime']
    search_fields = ['client_name']
    fields = ['product', 'client_name', 'phone', 'address']


admin.site.register(Order, OrderAdmin)