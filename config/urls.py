"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include,re_path
from ajax_select import urls as ajax_select_urls
from config import settings
from config.views import home, header, footer, handle_410_error

app_name = 'amor'
urlpatterns = [
    path('apanel/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('', home, name='home'),
    path('', include('components.urls', namespace='components')),
    path('', include('pages.urls', namespace='pages')),
    path('', include('blog.urls', namespace='blog')),
    path('', include('u_account.urls', namespace='account')),
    path('', include('product.urls', namespace='products')),
    path('', include('orders.urls', namespace='orders')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^ajax_select/', include(ajax_select_urls)),
    path('header/', header, name='header'),
    path('footer/', footer, name='footer'),
    path('410/', handle_410_error, name='handle_410_error'),
]

if settings.DEBUG:
    # add root static files
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # add media static files
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = 'jimbojet.views.handle_4040_error'
admin.site.site_header = "مدیریت وبگاه امرداد"
admin.site.site_title = "پنل مدیریت امرداد"
admin.site.index_title = "به امرداد خوش آمدید"
