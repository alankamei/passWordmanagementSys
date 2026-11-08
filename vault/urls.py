from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("vault/", views.vault_list, name="vault_list"),
    path("vault/new/", views.vault_create, name="vault_create"),
    path("vault/<int:pk>/", views.vault_detail, name="vault_detail"),
    path("vault/<int:pk>/edit/", views.vault_update, name="vault_update"),
    path("vault/<int:pk>/delete/", views.vault_delete, name="vault_delete"),
]