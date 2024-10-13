from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('edit-info/', views.PersonalInfoView.as_view(), name='edit_personal_info'),
    path('login/', views.login_m, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('forget-password', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('reset-password/<activation_code>', views.ResetPasswordView.as_view(), name='reset_password_page'),
    path('account-activation/<activation_code>', views.ActivateAccountView.as_view(), name='activate_account'),
    path('account-activation/', views.ActivateAccountView.as_view(), name='activate_account'),
    path('orders/', views.OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('invoice/<int:order_id>', views.show_invoice, name='invoice'),
]
