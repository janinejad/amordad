from django.urls import path
from .views import page,ContactUsView,send_email_address

app_name = 'pages'
urlpatterns = [
    path('page/<slug>', page, name='page'),
    path('contact-us/<slug>', ContactUsView.as_view(), name='contact_us'),
    path('send-email-address/', send_email_address, name='send_email_address'),
]
