from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [
    path('product/<int:id>/<product_name>/', views.product_single, name='product'),
    path('add_favorite/<int:product_id>/', views.add_favorite, name='add_favorite'),
    path('product-category/<slug:cat_s>/', views.products, name='product_category'),
    path('search/', views.products, name='search'),
    path('calculate-price/<int:id>/<int:qty>/', views.calculate_price, name='calculate_price'),

]
