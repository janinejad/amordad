import logging

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.contrib import admin
from django.urls import resolve

from .models import MenuList, Menu, ProductCatMenu
from django.forms import TextInput
from django.db import models


# Register your models here.


class MenuListInline(admin.TabularInline):
    model = MenuList
    extra = 0
    show_change_link = True
    formfield_overrides = {
        models.URLField: {'widget': TextInput(attrs={'size': '30'})},
        models.CharField: {'widget': TextInput(attrs={'size': '30'})},
        models.IntegerField: {'widget': TextInput(attrs={'size': '30'})},
    }


class MenuAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        setting_count = Menu.objects.all().count()
        if setting_count > 2:
            return False
        else:
            return True

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []
        return super(MenuAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = [MenuListInline]
        return super(MenuAdmin, self).change_view(request, object_id, form_url, extra_context)


@admin.register(ProductCatMenu)
class ProductCatMenuAdmin(AjaxSelectAdmin):
    list_display = ['__str__', 'parent_id', 'cat']
    list_filter = ['type']
    search_fields = ['title']
    form = make_ajax_form(ProductCatMenu, {
        'cat': 'cat',
    })

    class Meta:
        model = ProductCatMenu

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent_id":
            resolved = resolve(request.path_info)
            item = None
            if resolved.kwargs:
                item = ProductCatMenu.objects.get(pk=resolved.kwargs["object_id"]).id
            kwargs["queryset"] = ProductCatMenu.objects.exclude(pk=item)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Menu, MenuAdmin)
