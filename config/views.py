import math

from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.mail import send_mail

from blog.models import Post, Tag, PostCategory
from menus.models import ProductCatMenu, Menu
from pages.models import Page
from product.models import Product, ProductsCats, Brand
from settings.models import Setting, JsCode
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
def header_js_code(request):
    codes = JsCode.objects.get_header_tag_codes()
    context = {
        'codes': codes
    }
    return render(request, 'Shared/_HeaderJsCodes.html', context)


def footer_js_code(request):
    codes = JsCode.objects.get_footer_tag_codes()
    context = {
        'codes': codes
    }
    return render(request, 'Shared/_FooterJsCode.html', context)





class SitemapIndexView(TemplateView):
    content_type = 'application/xml'
    template_name = 'sitemap_index.xml'

    def get_context_data(self, **kwargs):
        sitemaps = [
            'https://jimboshop.ir/sitemap-products.xml',
            'https://jimboshop.ir/sitemap-pages.xml',
            'https://jimboshop.ir/sitemap-posts.xml',
            'https://jimboshop.ir/sitemap-post-categories.xml',
            'https://jimboshop.ir/sitemap-tags.xml',
            'https://jimboshop.ir/sitemap-product-category.xml',
            'https://jimboshop.ir/sitemap-product-brand.xml',
        ]
        context = {
            'sitemaps': sitemaps
        }
        return context


products = Product.objects.all()
product_count = products.count()

class ProductSitemapView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Product.objects.all()
        }
        return context



class TagsView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Tag.objects.all()
        }
        return context


class PostView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Post.objects.all()
        }
        return context


class PostCategoryView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': PostCategory.objects.all()
        }
        return context


class BrandView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Brand.objects.all()
        }
        return context
class ProductsCatsteeView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': ProductsCats.objects.all()
        }
        return context


class PageView(TemplateView):
    content_type = 'application/xml'
    template_name = 'shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Page.objects.all()
        }
        return context
