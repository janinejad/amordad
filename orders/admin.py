from django.contrib import admin
from django.db import models
from django.forms import TextInput, NumberInput, Select
from django.utils import timezone
from easy_select2 import select2_modelform
from jalali_date.admin import ModelAdminJalaliMixin

from orders.models import Order, OrderItem, OrderOtherPayment

OrderItemForm = select2_modelform(OrderItem, attrs={'width': '300px'})


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    form = OrderItemForm
    exclude = ('is_not_canceled', 'item',)
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '10'})},
        models.FloatField: {'widget': NumberInput(attrs={'style': 'width:70px;'})},
    }


class OrderOtherPaymentInline(ModelAdminJalaliMixin, admin.TabularInline):
    model = OrderOtherPayment
    extra = 0


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'invoice_info',
                'total_item_amount_before_discount_ir',
                'total_discount_ir',
                'total_item_amount_after_discount_ir',
                'total_tax_ir',
                'total_item_amount_with_tax_ir',
                'get_total_payed_amount_ir',
                'get_unpaid_ir',
                'jalali_order_date',
                'common_no',
                'full_address',
                'tax',
                'status_id',
                'order_description',
                'confirm',
            )
        }),
    )
    list_display = ['__str__', 'jalali_order_date']
    readonly_fields = ['invoice_info',
                       'total_item_amount_before_discount_ir',
                       'total_discount_ir',
                       'total_item_amount_after_discount_ir',
                       'total_tax_ir',
                       'total_item_amount_with_tax_ir',
                       'get_total_payed_amount_ir',
                       'get_unpaid_ir',
                       'jalali_order_date'
                       ]
    exclude = ['customer']
    list_filter = ['status_id']
    inlines = [OrderItemInline, OrderOtherPaymentInline]
