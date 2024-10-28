from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path('filter-products/', views.filterData, name='filterData'),
    path("import", views.importData, name='importData'),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("edit/<int:product_id>", views.edit_product, name='edit')
]