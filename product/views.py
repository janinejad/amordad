import math

from django.contrib import messages
from django.contrib.redirects.models import Redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from product.filters import SearchFilter
from product.models import Product, ProductFavorite, ProductInventory, ProductsCats, AttributeFilter, Brand, \
    AttributeItem
from settings.models import Setting


def product_single(request, id=None, product_name=None):
    is_favorite = False
    if request.user.is_authenticated:
        if request.user.is_staff:
            product = Product.objects.get_product_by_id(id, True)
        else:
            product = Product.objects.get_product_by_id(id)
    else:
        product = Product.objects.get_product_by_id(id)

    if product is None:
        redirected = Redirect.objects.filter(old_path__icontains=id).first()
        if redirected:
            return redirect(redirected.new_path)
        else:
            return redirect(reverse('handle_410_error'))
    if product.http_response_gone:
        return redirect(reverse('handle_410_error'))
    if request.user.is_authenticated:
        user_favorite = product.productfavorite_set.filter(user=request.user).first()
        if user_favorite:
            is_favorite = True
    context = {
        'is_favorite': is_favorite,
        'product': product,
    }
    return render(request, 'product-single.html', context)


def get_category_children(category):
    all_categories = []
    all_categories.append(category)

    def loop_category(cat):
        if cat.children.count() > 0:
            for c in cat.children.all():
                all_categories.append(c)
                loop_category(c)

    loop_category(category)
    return all_categories


def products(request, cat_s=None, *args, **kwargs):
    products = ProductInventory.objects.all()
    filter_list = []
    cat_obj = {}
    if cat_s:
        cat = ProductsCats.objects.all().filter(slug=cat_s).first()
        if not cat:
            return Http404
        products = products.filter(products__RootCategoryId__in=get_category_children(cat))
        attrs = AttributeFilter.objects.filter(category__slug=cat_s).distinct()
        attrs_list = []
        for attr in attrs:
            items = attr.attribute.attributeitem_set.filter(
                productattribute__products__productinventory__in=products).distinct()
            obj = {'attr': attr, 'items': items}
            attrs_list.append(obj)
        attribute_filters = request.GET.getlist('attr')
        for i in range(0, len(attribute_filters)):
            attribute_filters[i] = int(attribute_filters[i])
            obj = {'value': f"attr{attribute_filters[i]}", 'type': 'attr', 'id': attribute_filters[i],
                   'text': AttributeItem.objects.filter(id=attribute_filters[i]).first().item}
            filter_list.append(obj)

        cat_obj = {
            'attrs_list': attrs_list,
            'attribute_filters': attribute_filters,
            'cat': cat,
        }

    filter_search_form = SearchFilter(request.GET, queryset=products)
    products_brands = Brand.objects.all().filter(product__productinventory__in=products).distinct().order_by('title')
    products = filter_search_form.qs
    brand_filters = request.GET.getlist('brand')
    for i in range(0, len(brand_filters)):
        if brand_filters[i].isnumeric():
            brand_filters[i] = int(brand_filters[i])
            if products_brands.filter(id=brand_filters[i]).first():
                obj = {'value': f"brand{brand_filters[i]}", 'type': 'brand', 'id': brand_filters[i],
                       'text': products_brands.filter(id=brand_filters[i]).first().title}
                filter_list.append(obj)
    s = request.GET.get('q')
    if s:
        obj = {'value': 'searchBoxTxt', 'type': 'q', 'id': 's-filter-label',
               'text': s}
        filter_list.append(obj)
    paginator = Paginator(products, 40)
    page_number = request.GET.get("page")
    if not page_number:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context = {
        'filter_list': filter_list,
        'brand_filters': brand_filters,
        'brand_list': products_brands,
        'paginator': paginator,
        'page_obj': page_obj,
        'page_number': page_number,
        'cat_obj': cat_obj,
    }
    return render(request, 'products.html', context)


def favorite_status(request, *args, product_id, **kwargs):
    is_favorite = False
    if request.user.is_authenticated:
        product = Product.objects.filter(id=product_id).first()
        if product:
            user_favorite = product.productfavorite_set.filter(user=request.user).first()
            if user_favorite:
                is_favorite = True
    context = {
        'is_favorite': is_favorite
    }
    return render(request, 'shared/_favorite.html', context)


def add_favorite(request, *args, product_id, **kwargs):
    product = get_object_or_404(Product, id=product_id)
    if not request.user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        url = reverse('products:product', kwargs={'id': product_id, 'product_name': product.title})
        return JsonResponse({'url': url}, status=401)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        try:
            favorite = ProductFavorite.objects.filter(product=product, user=request.user).first()
            if favorite:
                favorite.delete()
            else:
                ProductFavorite.objects.create(product=product, user=request.user)
            return JsonResponse({}, status=200)
        except ProductFavorite.DoesNotExist:
            return JsonResponse({}, status=400)
    else:
        return JsonResponse({}, status=400)


def calculate_price(request, *args, id, qty, **kwargs):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        try:
            product: ProductInventory = ProductInventory.objects.filter(id=id).first()
            price = ''
            regular_price = ''
            if product:
                price = '{:,} تومان'.format(math.trunc(product.price * qty * product.unit))
                regular_price = product.price_ir()
            data = {
                'unit_d': product.unit,
                'unit': product.products.unit.title,
                'price': price,
                'regular_price': regular_price,
            }
            return JsonResponse(data, status=200)
        except ProductInventory.DoesNotExist:
            return JsonResponse({}, status=400)
    else:
        return JsonResponse({}, status=400)
