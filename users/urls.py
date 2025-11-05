from django.urls import path

from .views import CustomLoginView, RegisterView, UserListView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="list"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
]
