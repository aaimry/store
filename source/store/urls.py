from django.urls import path

from store.views import (ProductView, ProductCreateView, ProductDetailView, ProductUpdateView, ProductDeleteView,
                         BasketView, AddToBasketView, DeleteFromBasketView, MakeOrderView,UserOrderView, StatView)

app_name = 'store'

urlpatterns = [
    path('', ProductView.as_view(), name='index'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('basket/product/<int:pk>/add/', AddToBasketView.as_view(), name='basket_add'),
    path('basket/product/<int:pk>/delete/', DeleteFromBasketView.as_view(), name='basket_delete'),
    path('basket/order/', MakeOrderView.as_view(), name='make_order'),
    path('add/', ProductCreateView.as_view(), name='product_add'),
    path('check/<int:pk>', ProductDetailView.as_view(), name='product_check'),
    path('check/<int:pk>/update', ProductUpdateView.as_view(), name='product_update'),
    path('check/<int:pk>/delete', ProductDeleteView.as_view(), name='product_delete'),
    path('user/orders', UserOrderView.as_view(), name='user_order_list'),
    path('stat/', StatView.as_view(), name='stat')
]
