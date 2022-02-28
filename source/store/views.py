from copy import deepcopy
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, render

from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from store.forms import ProductsForm, SearchForm, OrderForm
from store.models import Products, Basket, Order, ProductBasket


class StatMixin:
    request = None

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.set_common_stat()
        self.set_page_time()
        return super().dispatch(request, *args, **kwargs)

    def set_common_stat(self):
        if 'stat' not in self.request.session:
            self.request.session['stat'] = {}
        stat = self.request.session.get('stat', {})
        if 'common_start_time' not in stat:
            stat['common_start_time'] = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        self.request.session['stat'] = stat

    def set_page_time(self):
        if 'stat' not in self.request.session:
            self.request.session['stat'] = {}
        stat = self.request.session.get('stat', {})
        if 'page' not in stat.keys():
            stat['page'] = {}
        page = stat['page']
        if self.request.path not in page:
            page[self.request.path] = {}
            page[self.request.path]['time'] = 0
        if 'new' in stat:
            old_time = page[stat['new']['path']]['time']
            time = (datetime.now() - datetime.strptime(stat['new']['start'], '%d/%m/%y %H:%M:%S')).seconds
            new_time = int(old_time) + time
            page[stat['new']['path']]['time'] = new_time
        else:
            stat['new'] = {}
        stat['new']['start'] = datetime.now().strftime('%d/%m/%y %H:%M:%S')
        stat['new']['path'] = self.request.path
        stat['page'] = page
        self.request.session['stat'] = stat


class StatView(StatMixin, View):
    def get(self, request, *args, **kwargs):
        common_time = 0
        if 'stat' not in self.request.session:
            self.request.session['stat'] = {}
        stat = self.request.session.get('stat', {})
        stat = deepcopy(stat)

        if 'common_start_time' in stat:
            start = datetime.strptime(stat['common_start_time'], '%d/%m/%y %H:%M:%S')
            end = datetime.now()
            common_time = str(end - start)

        if 'page' not in stat:
            stat['page'] = {}
        pages = stat['page']
        for key, values in pages.items():
            pages[key]['time'] = datetime.fromtimestamp(int(pages[key]['time'])).strftime("%H:%M:%S")
        if '/stat/' in pages:
            pages.pop('/stat/')
        return render(request, 'stat.html', context={'time': common_time, 'pages': pages})


class ProductView(StatMixin, ListView):
    model = Products
    context_object_name = "product"
    template_name = "products.html"
    paginate_by = 5
    paginate_orphans = 0

    def get(self, request, *args, **kwargs):
        self.form = self.get_form()
        self.search_value = self.get_search_value()
        print(f'session={self.request.session.get("stat", {})}')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.search_value:
            query = Q(title__icontains=self.search_value)
            queryset = queryset.filter(query)
        return queryset.order_by("title")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['form'] = SearchForm()
        if self.search_value:
            context['form'] = SearchForm(initial={"search": self.search_value})
            context['search'] = self.search_value
        return context

    def get_form(self):
        return SearchForm(self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data.get("search")


class ProductDetailView(StatMixin, DetailView):
    template_name = 'product_check.html'
    context_object_name = 'products_list'
    queryset = Products.objects.exclude(residue=0)
    model = Products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        check_list = get_object_or_404(Products, pk=kwargs.get('object').id)
        context['check_list'] = check_list
        return context


class ProductCreateView(PermissionRequiredMixin, StatMixin, CreateView):
    template_name = 'products_add.html'
    model = Products
    form_class = ProductsForm
    permission_required = 'store.add_products'

    def has_permission(self):
        return super().has_permission()


class ProductUpdateView(PermissionRequiredMixin, StatMixin, UpdateView):
    form_class = ProductsForm
    template_name = "update_product.html"
    model = Products
    context_object_name = 'product'
    permission_required = 'store.change_products'

    def has_permission(self):
        return super().has_permission()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(residue=0)
        return queryset


class ProductDeleteView(PermissionRequiredMixin, StatMixin, DeleteView):
    model = Products
    template_name = "product_delete.html"
    context_object_name = 'product'
    permission_required = 'store.delete_products'

    def has_permission(self):
        return super().has_permission()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.exclude(residue=0)
        return queryset

    def get_success_url(self):
        return reverse('store:index')


class BasketView(StatMixin, ListView):
    model = Basket
    context_object_name = "product"
    template_name = 'basket.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        total = 0
        for product in Basket.objects.all():
            total += product.get_sum()
        kwargs['total'] = total
        form = OrderForm()
        kwargs['form'] = form
        return super().get_context_data(**kwargs)


class AddToBasketView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Products, id=kwargs.get('pk'))
        try:
            basket = Basket.objects.get(product=product)
            if product.residue > 0:
                basket.quantity += 1
                basket.save()
                product.residue -= 1
                product.save()
                if 'basket' not in request.session:
                    request.session['basket'] = {}
                basket = request.session.get('basket', basket.pk)
                request.session['basket'] = basket
                messages.success(self.request, f'Добавлен товар :{product.title} ')
            else:
                messages.error(self.request, f'Невозможно добавить товар :{product.title}')
        except Basket.DoesNotExist:
            if product.residue != 0:
                basket = Basket.objects.create(product=product, quantity=1)
                basket.save()
                product.residue -= 1
                product.save()
            else:
                messages.error(self.request, f'Невозможно добавить товар : {product.title}')

        return redirect(request.META.get('HTTP_REFERER'))


class DeleteFromBasketView(DeleteView):
    model = ProductBasket
    success_url = reverse_lazy('store:basket')

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Products, pk=self.kwargs.get('pk'))
        basket = Basket.objects.get(product=product)
        if basket.quantity <= 1:
            basket.delete()
            messages.warning(self.request, f'Товар "{product.title}" удален')
        else:
            basket.quantity -= 1
            messages.warning(self.request, f'Товар "{product.title}" удален')
            basket.save()
            product.residue += 1
            product.save()
        return redirect('store:basket')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = Products.objects.get(id=self.object.product.id)
        products = request.session.get('products', {})
        products[product.title] = None
        request.session['products'] = products
        self.request.session['products'][product.title] = None
        self.object.delete()
        return redirect('store:basket')

class MakeOrderView(View):
    def post(self, request, *args, **kwargs):
        form = OrderForm(data=request.POST)
        if form.is_valid():
            order = Order.objects.create(
                client_name=form.cleaned_data.get('client_name'),
                phone=form.cleaned_data.get('phone'),
                address=form.cleaned_data.get('address')
            )
            if request.user.is_authenticated:
                order.user = request.user
                order.save()

            for product in Basket.objects.all():
                product_order = ProductBasket.objects.create(order=order, product=product.product,
                                                             quantity=product.quantity)
                product_order.save()

            Basket.objects.all().delete()
            return redirect('store:index')


class UserOrderView(LoginRequiredMixin, StatMixin, ListView):
    template_name = 'user_orders.html'
    model = Order
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = self.request.user.order.all().order_by('-datetime')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = ProductBasket.objects.all()
        context['product'] = product
        return context
