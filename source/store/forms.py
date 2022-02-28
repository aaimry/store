from django import forms
from store.models import CATEGORY_CHOICES, Products, Basket, Order


class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        exclude = []


class SearchForm(forms.Form):
    search = forms.CharField(max_length=30, required=False, label="Найти")


class AddToBasketForm(forms.ModelForm):
    class Meta:
        model = Basket
        exclude = []


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['product', 'user']