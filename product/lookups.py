from ajax_select import register, LookupChannel
from django.db.models import Q

from .models import AttributeItem, Product, ProductGallery, ProductAttribute, Attribute, ProductsCats, Brand


@register('attributeItem')
class TagsLookup(LookupChannel):
    model = AttributeItem

    def get_query(self, q, request):
        lookup = Q(attribute__title__icontains=q) | Q(item__icontains=q)
        return self.model.objects.filter(lookup)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('attribute')
class TagsLookup(LookupChannel):
    model = Attribute

    def get_query(self, q, request):
        lookup = Q(title__icontains=q)
        return self.model.objects.filter(lookup)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('cat')
class CatLookup(LookupChannel):
    model = ProductsCats

    def get_query(self, q, request):
        return self.model.objects.filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('brand')
class BrandLookup(LookupChannel):
    model = Brand

    def get_query(self, q, request):
        return self.model.objects.filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('product')
class VariantsLookup(LookupChannel):
    model = Product

    def get_query(self, q, request):
        return self.model.objects.filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('image_id')
class VariantsLookup(LookupChannel):
    model = ProductGallery

    def get_query(self, q, request):
        return self.model.objects.filter(title__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item


@register('product_attribute')
class VariantsLookup(LookupChannel):
    model = ProductAttribute

    def get_query(self, q, request):
        return self.model.objects.filter(attributeItem__item__icontains=q)

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % item
