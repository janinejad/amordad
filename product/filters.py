import django_filters
from django import forms
from product.models import *
from django.db.models import Q


class SearchFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method='product_name_filter')
    brand = django_filters.ModelMultipleChoiceFilter(
        field_name='products__brandId',
        queryset=Brand.objects.all(),
        label="Brands", conjoined=False
    )
    attr = django_filters.ModelMultipleChoiceFilter(
        field_name='products__productattribute__attributeItem',
        queryset=AttributeItem.objects.all(),
        label="attr", conjoined=False
    )

    class Meta:
        model = ProductInventory
        fields = ('q', 'brand', 'attr',)

    def product_name_filter(self, queryset, name, value):
        list_q = value.split(' ')
        products = queryset.all()
        for q in list_q:
            lookup = Q(products__title__icontains=q) | Q(products__Description__icontains=q) | Q(
                products__brandId__title__icontains=q) | Q(products__product__RootCategoryId__title__icontains=q)
            products = products.filter(lookup)
        products = products.filter(products__active=True)
        return products
