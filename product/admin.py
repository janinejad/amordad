import admin_thumbnails
from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin, AjaxSelectAdminTabularInline
from django.contrib import admin
from easy_select2.utils import select2_modelform
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportMixin
from product.models import Product, ProductGallery, Brand, ProductsCats, ProductAttribute, Attribute, AttributeItem, \
    ProductInventory, ProductFavorite, ProductMainFeature, GroupAttribute, Units, AttributeFilter, ProductExperts
from django.forms import TextInput
from django.db import models

# Register your models here.
ProductForm = select2_modelform(Product, attrs={'width': '300px'})
ProductAttrForm = select2_modelform(ProductAttribute, attrs={'width': '300px'})
AttributeItemForm = select2_modelform(AttributeItem, attrs={'width': '300px'})
GroupAttributeForm = select2_modelform(GroupAttribute, attrs={'width': '200px'})
AttributeForm = select2_modelform(Attribute, attrs={'width': '200px'})


@admin.register(Units)
class UnitsAdmin(admin.ModelAdmin):
    list_display = ['__str__']


class ProductMainFeatureInline(admin.TabularInline):
    model = ProductMainFeature
    extra = 1
    show_change_link = True


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    show_change_link = True


class ProductAttrInline(AjaxSelectAdminTabularInline):
    model = ProductAttribute
    form = make_ajax_form(ProductAttribute, {
        'attributeItem': 'attributeItem'
    })
    extra = 0


@admin.register(ProductAttribute)
class ProductAttributeAdmin(AjaxSelectAdmin):
    form = make_ajax_form(ProductAttribute, {
        'attributeItem': 'attributeItem',
        'products': 'product',
    })
    list_display = ['__str__', 'products']
    search_fields = ['attributeItem__attribute__title', 'products__RootCategoryId__title', 'attributeItem__item',
                     'attributeItem__attribute__group_attribute__title']
    list_filter = ['products__RootCategoryId']


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['slug', 'title']
    list_display = ['__str__', 'slug', 'image_tag', 'review_reason', 'active',
                    'RootCategoryId', 'created_at']
    list_filter = [('user', admin.RelatedOnlyFieldListFilter), 'active', 'brandId', 'RootCategoryId']
    form = ProductForm
    filter_horizontal = ('similar_products',)
    inlines = [ProductMainFeatureInline, ProductAttrInline, ProductGalleryInline]
    list_per_page = 33
    date_hierarchy = "created_at"
    exclude = ('user',)
    resource_class = ProductResource

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = [ProductAttrInline, ProductGalleryInline, ProductMainFeatureInline]
        self.exclude = ('user', 'active', 'review_reason',)
        return super(ProductAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [ProductAttrInline, ProductGalleryInline, ProductMainFeatureInline]
        if request.user.is_superuser or request.user.is_content_manager:
            self.exclude = (
                'user',)
        else:
            self.exclude = ('user', 'active', 'review_reason',)
        return super(ProductAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()
        super().save_model(request, obj, form, change)

    class Meta:
        model = Product


@admin_thumbnails.thumbnail('image', alias='تصویر')
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_tag', 'is_active', 'review_reason', 'display_order', 'url_tag']
    list_editable = ['display_order']
    list_filter = ['is_active']
    search_fields = ['title', 'user__last_name', 'user__mobile']

    class Meta:
        model = Brand

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'review_reason', 'is_active',)
        return super(BrandAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser or request.user.is_content_manager:
            self.exclude = ('user',)
        else:
            self.exclude = ('user', 'review_reason', 'is_active',)
        return super(BrandAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_content_manager:
            return qs
        return qs.filter(user=request.user)


class ProductsCatResource(resources.ModelResource):
    class Meta:
        model = ProductsCats
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True


ProductCategoryForm = select2_modelform(ProductsCats, attrs={'width': '300px'})


@admin.register(ProductsCats)
class ProductsCatsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_image", "parent_id", "url_tag", "is_active", "has_products", "middle_cat"]
    search_fields = ['title']
    filter_horizontal = ['experts']
    form = ProductCategoryForm
    exclude = ['depth',]
    resource_class = ProductsCatResource

    class Meta:
        model = ProductsCats


class AttributeAdminResource(resources.ModelResource):
    class Meta:
        model = Attribute


class AttributeItemInLine(admin.TabularInline):
    model = AttributeItem
    extra = 0
    show_change_link = True
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '20'})},
    }


@admin.register(Attribute)
class AttributeAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['title']
    inlines = [AttributeItemInLine]
    resource_class = AttributeAdminResource
    form = AttributeForm

    class Meta:
        model = Attribute


class ProductInventoryResource(resources.ModelResource):
    class Meta:
        model = ProductInventory
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True


@admin.register(ProductInventory)
class ProductInventoryAdmin(ImportExportModelAdmin):
    list_display = ['__str__', 'quantity', 'regular_price']
    search_fields = ['products__title']
    list_editable = ['regular_price', 'quantity']
    list_filter = ['status', 'weight']
    resource_class = ProductInventoryResource


@admin.register(ProductFavorite)
class ProductFavoriteAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    search_fields = ['product__title']


class AttributeInLine(admin.TabularInline):
    model = Attribute
    extra = 0
    show_change_link = True


class GroupAttributeResource(resources.ModelResource):
    class Meta:
        model = GroupAttribute


@admin.register(GroupAttribute)
class GroupAttributeAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
    inlines = [AttributeInLine]
    form = GroupAttributeForm
    resource_class = GroupAttributeResource

    class Meta:
        model = GroupAttribute


class AttributeItemResource(resources.ModelResource):
    class Meta:
        model = AttributeItem


@admin.register(AttributeItem)
class AttributeItemAdmin(ExportMixin, AjaxSelectAdmin):
    list_display = ['__str__', 'attribute', 'display_order']
    search_fields = ['item', 'attribute__title']
    list_filter = ['attribute', 'attribute__group_attribute']
    fieldsets = (
        ('مقدار ویژگی', {
            'fields': ('item', 'attribute', 'display_order', 'image',)
        }),
    )

    resource_class = AttributeItemResource
    form = make_ajax_form(AttributeItem, {
        'attribute': 'attribute',
    })

    class Meta:
        model = AttributeItem


class AttributeFilterAdmin(AjaxSelectAdmin):
    list_display = ['__str__', 'category', 'attribute', 'display_order']
    list_filter = ['category']
    form = make_ajax_form(AttributeFilter, {
        'attribute': 'attribute',
        'category': 'cat',
    })

    class Meta:
        model = AttributeFilter


admin.site.register(AttributeFilter, AttributeFilterAdmin)


@admin.register(ProductExperts)
class ProductExpertsAdmin(admin.ModelAdmin):
    list_display = ['__str__']
