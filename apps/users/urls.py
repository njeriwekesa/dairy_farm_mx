from django.urls import path
from . import views
from .views import RegisterView

urlpatterns = [
    path("", views.UserListView.as_view(), name="user-list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("register/", RegisterView.as_view(), name="register"),

]
