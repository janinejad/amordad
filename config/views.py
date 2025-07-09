import math

from django.core.cache import cache
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
    cats = cache.get('cats')
    if not cats:
        cats = ProductsCats.objects.get_slider_cats()
        cache.set('cats', cats, 60 * 5)
    products = Product.objects.newest_products()[:4]
    posts = cache.get('posts')
    if not posts:
        posts = Post.objects.all()[:6]
        cache.set('posts', posts, 60 * 5)
    context = {
        'cats': cats,
        'products': products,
        'posts': posts,
    }
    return render(request, 'Home.html', context)


def header(request):
    register_form = RegisterForm()
    login_form = LoginForm()
    forgo_password = ForgotPasswordForm()
    cats_menu = cache.get('cats_menu')
    if not cats_menu:
        cats_menu = ProductCatMenu.objects.filter(parent_id=None)
        cache.set('cats_menu', cats_menu, 60 * 5)
    context = {
        'cats_menu': cats_menu,
        'register_form': register_form,
        'login_form': login_form,
        'forgo_password': forgo_password,
    }
    return render(request, 'Shared/_Header.html', context)


def footer(request):
    menus: Menu = Menu.objects.all()
    context = {
        'menus': menus,
    }

    return render(request, 'Shared/_Footer.html', context)


def handle_410_error(request):
    return render(request, '404.html', status=404)


def header_js_code(request):
    header_codes = cache.get('header_codes')
    if not header_codes:
        header_codes = JsCode.objects.get_header_tag_codes()
        cache.set('header_codes', header_codes, 60 * 5)
    context = {
        'codes': header_codes
    }
    return render(request, 'Shared/_HeaderJsCodes.html', context)


def footer_js_code(request):
    codes = cache.get('codes')
    if not codes:
        codes = JsCode.objects.get_trusted_symbols()
        cache.set('codes', codes, 60 * 5)
    context = {
        'codes': codes
    }
    return render(request, 'Shared/_FooterJsCode.html', context)


class SitemapIndexView(TemplateView):
    content_type = 'application/xml'
    template_name = 'sitemap_index.xml'

    def get_context_data(self, **kwargs):
        sitemaps = [
            {'location': 'https://amordadsteel.com/sitemap-products.xml'},
            {'location': 'https://amordadsteel.com/sitemap-pages.xml'},
            {'location': 'https://amordadsteel.com/sitemap-posts.xml'},
            {'location': 'https://amordadsteel.com/sitemap-post-categories.xml'},
            {'location': 'https://amordadsteel.com/sitemap-tags.xml'},
            {'location': 'https://amordadsteel.com/sitemap-product-category.xml'},
        ]
        context = {
            'sitemaps': sitemaps
        }
        return context


class ProductSitemapView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Product.objects.all()
        }
        return context


class TagsView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Tag.objects.all()
        }
        return context


class PostView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Post.objects.all()
        }
        return context


class PostCategoryView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': PostCategory.objects.all()
        }
        return context


class ProductsCatsteeView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': ProductsCats.objects.all()
        }
        return context


class PageView(TemplateView):
    content_type = 'application/xml'
    template_name = 'Shared/custom-sitemap.xml'

    def get_context_data(self, **kwargs):
        context = {
            'locations': Page.objects.all()
        }
        return context


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import default_storage
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('file')
        path = default_storage.save(f'uploads/{image.name}', image)
        image_url = os.path.join('/public/media/', path)
        return JsonResponse({'location': image_url})

