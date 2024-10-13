from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update_cart/<int:item_id>', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:variant_id>', views.cart_remove, name='remove-from-cart'),
    path('remove-items/', views.remove_items, name='remove_items'),
    path('shopping-complete/', views.complete_shopping, name='complete_shopping'),
    path('cart/', views.cart, name='cart'),
]
