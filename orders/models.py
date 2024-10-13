import math

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from jalali_date import datetime2jalali

from product.models import ProductInventory
from u_account.models import User


# Create your models here.

class OrderManager(models.Manager):
    def all(self):
        lookup = ~Q(status_id=0)
        return self.get_queryset().filter(lookup, orderitem__is_not_canceled=True).distinct().order_by(
            '-order_date')

    def all_with_in_cart(self):
        return self.get_queryset().filter(orderitem__is_not_canceled=True).distinct().order_by(
            '-order_date')


class Order(models.Model):
    STATUS = (
        ('0', 'سبد خرید'),
        ('1', 'در انتظار پرداخت'),
        ('2', 'پرداخت شده'),
        ('3', 'پیش پرداخت'),
        ('4', 'لغو شده'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='مشتری')
    common_no = models.PositiveIntegerField(default=0, verbose_name='شماره فاکتور سیستم حسابداری')
    full_address = models.TextField(max_length=1000, blank=True, null=True, verbose_name='آدرس کامل')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ سفارش')
    tax = models.FloatField(default=9, verbose_name='درصد مالیات بر ارزش افزوده')
    status_id = models.CharField(max_length=10, default='0', choices=STATUS, verbose_name='وضعیت')
    order_description = models.TextField(max_length=1000, blank=True, null=True, verbose_name='توضیحات سفارش')
    confirm = models.BooleanField(default=False, verbose_name='وضعیت ارسال سفارشات به انبار')
    objects = OrderManager()

    def __str__(self):
        return f"{self.customer.get_full_name()} - شماره سفارش {self.id}"

    class Meta:
        verbose_name_plural = "سفارشات"
        verbose_name = 'سفارش'

    def invoice_info(self):
        info = ""
        if self.invoice.is_official:
            info = f"مشخصات حقوقی : {self.invoice.organization_name} - شماره ثبت {self.invoice.firm_no} - کد اقتصادی : {self.invoice.firm_economical_no} - شناسه ملی : {self.invoice.firm_national_id} - آدرس : {self.invoice.full_address}"
        else:
            info = f"نام : {self.invoice.full_name} - کد ملی : {self.invoice.national_code}"
        return info

    invoice_info.short_description = "مشخصات فاکتور"
    def get_status(self):
        match self.status_id:
            case '0':
                return 'سبد خرید'
            case '1':
                return 'در انتظار پرداخت'
            case '2':
                return 'پرداخت شده'
            case '3':
                return 'پیش پرداخت'
            case '4':
                return 'لغو شده'

    def get_total_payed_amount(self):
        return sum([i.amount for i in self.orderotherpayment_set.all()])

    def total_item_amount_before_discount(self):
        return sum([(i.product_count * i.product_price) for i in self.orderitem.all_without_canceled()])

    def total_item_amount_after_discount(self):
        return self.total_item_amount_before_discount() - sum(
            [i.product_count * i.total_discount for i in self.orderitem.all_without_canceled()])

    def total_discount(self):
        return sum(
            [i.product_count * i.total_discount for i in self.orderitem.all_without_canceled()])

    def total_item_amount_with_tax(self):
        return self.total_item_amount_after_discount() + self.total_tax()

    def total_tax(self):
        return sum([(i.product_count * i.tax) for i in self.orderitem.all_without_canceled()])

    def get_unpaid(self):
        amount = self.total_item_amount_with_tax() - self.get_total_payed_amount()
        return amount

    def total_item_amount_before_discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.total_item_amount_before_discount()))

    def invoice_total_item_amount_before_discount_ir(self):
        return '{:,}'.format(math.trunc(self.total_item_amount_before_discount() * 10))

    def total_item_amount_after_discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.total_item_amount_after_discount()))

    def invoice_total_item_amount_after_discount_ir(self):
        return '{:,}'.format(math.trunc(self.total_item_amount_after_discount() * 10))

    def total_discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.total_discount()))

    def invoice_total_discount_ir(self):
        return '{:,}'.format(math.trunc(self.total_discount() * 10))

    def total_tax_ir(self):
        return '{:,} تومان'.format(math.trunc(self.total_tax()))

    def invoice_total_tax_ir(self):
        return '{:,}'.format(math.trunc(self.total_tax()))

    def total_item_amount_with_tax_ir(self):
        return '{:,} تومان'.format(math.trunc(self.total_item_amount_with_tax()))

    def invoice_total_item_amount_with_tax_ir(self):
        return '{:,}'.format(math.trunc(self.total_item_amount_with_tax() * 10))

    def get_unpaid_ir(self):
        return '{:,} تومان'.format(math.trunc(self.get_unpaid()))

    def get_total_payed_amount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.get_total_payed_amount()))

    def jalali_order_date(self):
        jalalidate = datetime2jalali(self.order_date).strftime('%Y/%m/%d _ %H:%M:%S')
        return jalalidate

    def jalali_order_only_date(self):
        jalalidate = datetime2jalali(self.order_date).strftime('%Y/%m/%d')
        return jalalidate

    total_item_amount_before_discount_ir.short_description = "مبلغ کل قبل از تخفیف"
    total_discount_ir.short_description = "مبلغ تخفیف"
    total_item_amount_after_discount_ir.short_description = "مبلغ کل بعد از تخفیف"
    total_tax_ir.short_description = "مبلغ مالیات بر ارزش افزوده"
    total_item_amount_with_tax_ir.short_description = "مبلغ کل با احتساب مالیات"
    get_total_payed_amount_ir.short_description = "مبلغ پرداخت شده"
    get_unpaid_ir.short_description = "مانده فاکتور"
    jalali_order_date.short_description = "تاریخ سفارش"


def order_pre_post_save_receiver(sender, instance, *args, **kwargs):
    from settings.models import Financials
    st: Financials = Financials.objects.first()
    tax = 10
    if st:
        tax = st.tax
    instance.tax = tax


pre_save.connect(order_pre_post_save_receiver, sender=Order)


class OrderOtherPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ پرداخت')
    payment_memo = models.CharField(max_length=250, blank=True, null=True, verbose_name='توضیحات پرداخت')
    amount = models.FloatField(default=0, verbose_name='مبلغ پرداختی')

    class Meta:
        verbose_name_plural = 'سایر پرداختیهای سفارش'
        verbose_name = 'پرداختی سفارش'


class OrderItemManager(models.Manager):
    def all_without_canceled(self):
        return self.get_queryset().filter(is_not_canceled=True)

    def get_user_total_sales(self, user):
        lookup = (Q(order__referee=user) | Q(order__referee__parent=user)) & ~Q(order__customer=user)
        order_items = self.get_queryset().filter(lookup)
        return order_items

    def get_referrals(self, user):
        lookup = Q(order__referee=user) & ~Q(order__customer=user)
        order_items = self.get_queryset().filter(lookup, order__status_id__in=[7, 2, 3])
        return order_items

    def get_unapplied_referrals(self, user):
        lookup = Q(commission__isnull=True) | Q(commission__flag=False)
        return self.get_referrals(user).filter(lookup)

    def all_in_cart(self):
        return self.get_queryset().filter(is_not_canceled=True, order__status_id=0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orderitem', on_delete=models.CASCADE, verbose_name='شماره سفارش')
    variant = models.ForeignKey(ProductInventory, on_delete=models.PROTECT, null=True, verbose_name='نام محصول')
    product_price = models.FloatField(default=0, verbose_name='مبلغ')
    supplement_price = models.FloatField(default=0, verbose_name='قیمت تامین')
    tax = models.FloatField(default=0, verbose_name='مالیات بر ارزش افزوده')
    item = models.CharField(max_length=500, verbose_name='آیتم سفارش')
    total_discount = models.FloatField(default=0, verbose_name='تخفیف')
    product_count = models.PositiveIntegerField(verbose_name='تعداد')
    is_not_canceled = models.BooleanField(default=True, verbose_name='وضعیت')
    objects = OrderItemManager()

    def item_amount_before_discount(self):
        return self.product_count * self.product_price

    def item_amount_after_discount(self):
        return self.item_amount_before_discount() - (self.product_count * self.total_discount)

    def discount(self):
        return self.product_count * self.total_discount

    def item_amount_with_tax(self):
        return self.item_amount_after_discount() + self.item_tax()

    def item_tax(self):
        return self.product_count * self.tax

    def item_amount_before_discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.item_amount_before_discount()))

    def item_amount_after_discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.item_amount_after_discount()))

    def discount_ir(self):
        return '{:,} تومان'.format(math.trunc(self.discount()))

    def tax_ir(self):
        return '{:,} تومان'.format(math.trunc(self.item_tax()))

    def item_amount_with_tax_ir(self):
        return '{:,} تومان'.format(math.trunc(self.item_amount_with_tax()))

    def product_price_ir(self):
        return '{:,} تومان'.format(math.trunc(self.product_price))

    def invoice_product_price_ir(self):
        return '{:,}'.format(math.trunc(self.product_price * 10))

    def invoice_item_amount_before_discount_ir(self):
        return '{:,}'.format(math.trunc(self.item_amount_before_discount() * 10))

    def invoice_item_amount_after_discount_ir(self):
        return '{:,}'.format(math.trunc(self.item_amount_after_discount() * 10))

    def invoice_discount_ir(self):
        return '{:,}'.format(math.trunc(self.discount() * 10))

    def invoice_tax_ir(self):
        return '{:,}'.format(math.trunc(self.item_tax() * 10))

    def invoice_item_amount_with_tax_ir(self):
        return '{:,}'.format(math.trunc(self.item_amount_with_tax() * 10))

    class Meta:
        verbose_name_plural = 'آیتمهای سفارشات'
        verbose_name = 'آیتم'
        ordering = ('-id',)

    def __str__(self):
        return str(self.variant)

    def item_price(self):
        amount = self.product_count * self.product_price
        return amount

    def order_date_ir(self):
        jalalidate = datetime2jalali(self.order.order_date).strftime('%Y/%m/%d _ %H:%M:%S')
        return jalalidate

    order_date_ir.short_description = 'تاریخ سفارش'


def order_item_pre_post_save_receiver(sender, instance, *args, **kwargs):
    instance.item = instance.variant.__str__()
    instance.tax = (instance.variant.regular_price - instance.total_discount) * (instance.order.tax / 100)
    if instance.order.status_id == 0:
        instance.supplement_price = instance.variant.supplement_price


pre_save.connect(order_item_pre_post_save_receiver, sender=OrderItem)


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, verbose_name='سفارش')
    invoice_date = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت سفارش')
    national_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='کد ملی')
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name='کد پستی')
    full_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام کامل')
    first_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام')
    last_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام خانوادگی')
    mobile = models.CharField(max_length=11, blank=True, null=True, verbose_name='موبایل')
    is_official = models.BooleanField(default=False, verbose_name='شخصیت حقوقی')
    organization_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='نام سازمان')
    firm_no = models.CharField(max_length=20, blank=True, null=True, verbose_name='شماره ثبت')
    firm_national_id = models.CharField(max_length=11, blank=True, null=True, verbose_name='شناسه ملی')
    firm_economical_no = models.CharField(max_length=12, blank=True, null=True, verbose_name='کد اقتصادی')
    full_address = models.TextField(max_length=700, null=True, blank=True, verbose_name='آدرس کامل')
    tel_no = models.CharField(max_length=12, null=True, blank=True, verbose_name='شماره تماس')

    def __str__(self):
        return f"{self.id}-{self.full_name}"

    class Meta:
        verbose_name_plural = 'فاکتورها'
        verbose_name = 'فاکتور'
