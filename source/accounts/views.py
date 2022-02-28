from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from accounts.forms import MyUserCreationForm
from store.models import Basket


class RegisterView(CreateView):
    model = User
    template_name = "registration.html"
    form_class = MyUserCreationForm

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if not next_url:
            next_url = self.request.POST.get('next')
        if not next_url:
            next_url = reverse('tracker:index_project')
        return next_url


class BasketClearLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        basket = get_object_or_404(Basket, pk=self.request.basket.pk)
        basket = request.session.get('basket', basket.pk)
        basket[basket] = None
        request.session['basket'] = basket
        basket.clear()
        return super().dispatch(request, *args, **kwargs)
