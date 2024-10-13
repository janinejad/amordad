from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.mail import send_mail

from blog.models import Post
from menus.models import ProductCatMenu, Menu
from product.models import Product, ProductsCats
from settings.models import Setting
from u_account.forms import RegisterForm, LoginForm, ForgotPasswordForm


def home(request):
    st = Setting.objects.first()
    cats = ProductsCats.objects.get_slider_cats()
    products = Product.objects.newest_products()[:4]
    posts = Post.objects.all()[:6]
    context = {
        'cats': cats,
        'products': products,
        'posts': posts,
    }
    if st:
        context["st"] = st

    return render(request, 'Home.html', context)


def header(request):
    register_form = RegisterForm()
    login_form = LoginForm()
    forgo_password = ForgotPasswordForm()
    cats_menu = ProductCatMenu.objects.filter(parent_id=None)
    about_us = ""
    logo = ""
    st: Setting = Setting.objects.first()
    if st:
        about_us = st.about_us_page.get_abs_url()
        logo = st.brand_logo.url
    context = {
        'cats_menu': cats_menu,
        'register_form': register_form,
        'login_form': login_form,
        'forgo_password': forgo_password,
        'about_us': about_us,
        'logo': logo,
    }
    return render(request, 'Shared/_Header.html', context)


def footer(request):
    menus: Menu = Menu.objects.all()
    st: Setting = Setting.objects.first()
    context = {
        'menus': menus,
        'st':st
    }

    return render(request, 'Shared/_Footer.html', context)


def handle_410_error(request):
    return render(request, '404.html', status=410)
