from django.contrib.auth.views import LoginView
from django.urls import path

from accounts.views import RegisterView, BasketClearLogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', BasketClearLogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
]

