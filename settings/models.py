import math

from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from extensions.utils import get_filename_ext, delete_tasks
from pages.models import Page
from product.models import Attribute


# Create your models here.


def upload_image_setting_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{instance.id}-{timezone.now()}{ext}"
    return f"Settings/{file_name}"


class Financials(models.Model):
    tax = models.FloatField(default=10, verbose_name='مالیات بر ارزش افزوده')

    def __str__(self):
        return 'تنظیمات مالی'

    class Meta:
        verbose_name_plural = 'تنظیمات مالی'
        verbose_name = 'تنظیمات'


class CompanyInfo(models.Model):
    juridical_personality_title = models.CharField(max_length=150, null=True, blank=True,
                                                   verbose_name='عنوان شخصیت حقوقی')
    juridical_personality_address = models.TextField(null=True, blank=True, verbose_name='آذرس شخصیت حقوقی')
    economic_code = models.CharField(max_length=12, null=True, blank=True, verbose_name='کد اقتصادی')
    national_id = models.CharField(max_length=12, null=True, blank=True, verbose_name='شناسه ملی')
    postal_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد پستی')
    firm_no = models.CharField(max_length=10, null=True, blank=True, verbose_name='شماره ثبت')
    tel_no = models.CharField(max_length=150, verbose_name='شماره تماس', null=True)
    signature = models.ImageField(upload_to=upload_image_setting_path, verbose_name='تصویر امضاء')
    has_official_bill = models.BooleanField(default=False, verbose_name='وضعیت ارائه فاکتور رسمی')
    warehouse_address = models.TextField(null=True, blank=True, verbose_name='آذرس انبار')

    def __str__(self):
        return 'اطلاعات شرکت'

    class Meta:
        verbose_name_plural = 'اطلاعات شرکت'
        verbose_name = 'اطلاعات شرکت'


class SMSSettingManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(is_active=True)


class SMSSetting(models.Model):
    APIS = (
        ('MELIPAYAMAR', 'ملی پیامک'),
        ('RAZPAYAMAK', 'راز پیامک'),
        ('None', 'تنظیم نشده'),
    )
    title = models.CharField(max_length=150, verbose_name='عنوان وب سرویس')
    api_type = models.CharField(max_length=50, default='None', choices=APIS, verbose_name='وب سرویس')
    is_active = models.BooleanField(default=False, verbose_name='وضعیت')
    code_cancel = models.IntegerField(default=1, verbose_name='کد متن مهلت پرداخت سفارش')
    cancel_order_is_active = models.BooleanField(default=True, verbose_name='وضعیت ارسال پیامک مهلت پرداخت')
    code_otp = models.IntegerField(default=1, verbose_name='کد متن کد یک بار مصرف')
    code_pending_payment = models.IntegerField(default=1, verbose_name='کد متن پیامک در انتظار پرداخت')
    pending_payment_is_active = models.BooleanField(default=True, verbose_name='وضعیت ارسال پیامک در انتظار پرداخت')
    code_completed_payment = models.IntegerField(default=1, verbose_name='کد متن پیامک در تکمیل شدن پرداخت')
    completed_payment_is_active = models.BooleanField(default=True,
                                                      verbose_name='وضعیت ارسال پیامک در تکمیل شدن پرداخت')
    code_deposit_completed_payment = models.IntegerField(default=1, verbose_name='کد متن پیامک در تکمیل شدن پیش پرداخت')
    deposit_completed_payment_is_active = models.BooleanField(default=True,
                                                              verbose_name='وضعیت ارسال پیامک در تکمیل شدن  پیش پرداخت')
    username = models.CharField(max_length=250, null=True, blank=True, verbose_name='نام کاربری')
    password = models.CharField(max_length=250, null=True, blank=True, verbose_name='رمز عبور')
    api_link = models.URLField(null=True, blank=True, verbose_name='لینک وب سرویس')
    objects = SMSSettingManager()

    class Meta:
        verbose_name_plural = 'تنظیمات پیامک'
        verbose_name = 'تنظیمات پیامک'

    def __str__(self):
        return self.title


class Setting(models.Model):
    site_title = models.CharField(max_length=150, verbose_name="عنوان فروشگاه")
    brand_name = models.CharField(max_length=50, verbose_name="عنوان برند")
    siteUrl = models.URLField(max_length=250, null=True, blank=True, verbose_name="آدرس سایت")
    opt_time = models.IntegerField(default=0, verbose_name='زمان انقضای کد تایید',
                                   help_text='یه ثانیه باشد')
    order_cancel_time = models.IntegerField(default=360, verbose_name='مهلت پرداخت سفارش')
    brand_logo = models.FileField(upload_to=upload_image_setting_path, null=False, verbose_name='لوگوی سایت')
    site_slogan = models.CharField(max_length=250, null=True, verbose_name="شعار فروشگاه")
    site_description = models.TextField(max_length=500, null=True, verbose_name="توضیحات کوتاه سایت")
    work_time_text = models.TextField(max_length=500, null=True, verbose_name="متن ساعات کاری فروشگاه ")
    copy_right_text = models.TextField(max_length=500, null=True, verbose_name="متن کپی رایت ")
    address = models.TextField(max_length=500, null=True, verbose_name="آدرس")
    tel_no = models.CharField(max_length=150, verbose_name='شماره تماس', null=True)
    whatsapp_num = models.CharField(max_length=150, verbose_name='شماره واتس اپ', null=True)
    email_address = models.EmailField(max_length=254, null=True, blank=True, verbose_name='آدرس ایمیل')
    first_page_tag_line = models.CharField(max_length=250, null=True, blank=True, verbose_name='شعار صفحه اول')
    first_page_description = models.TextField(max_length=500, null=True, blank=True, verbose_name="توضیحات صفحه اول")
    whatsapp_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک واتس اپ")
    telegram_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک تلگرام")
    instagram_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک اینستاگرام")
    twitter_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک توییتر")
    facebook_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="لینک فیسبوک")
    about_us_page = models.ForeignKey(Page, null=True, related_name='about_us_page', blank=True,
                                      on_delete=models.SET_NULL, verbose_name='صفحه تماس با ما')
    main_page = models.ForeignKey(Page, null=True, related_name='main_page', blank=True, on_delete=models.SET_NULL,
                                  verbose_name='صفحه اصلی')
    terms_conditions = models.ForeignKey(Page, null=True, related_name='terms_condition_page', blank=True, on_delete=models.SET_NULL,
                                  verbose_name='صفحه قوانین')
    meta_title = models.CharField(max_length=600, null=True, blank=True, verbose_name='عنوان سئو صفحه اصلی')
    meta_desc = models.CharField(max_length=600, null=True, blank=True, verbose_name='توضیحات سئو صفحه اصلی')
    keywords = models.TextField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی صفحه اصلی')

    def __str__(self):
        return "تنظیمات عمومی"

    class Meta:
        verbose_name_plural = "تظیمات عمومی"
        verbose_name = "تظیمات"

    def get_order_cancel_time(self):
        return math.trunc(self.order_cancel_time / 60)


def setting_post_save_save_receiver(sender, instance, *args, **kwargs):
    from orders.Tasks import automatic_update
    delete_tasks('orders.Tasks.automatic_update')
    automatic_update()


post_save.connect(setting_post_save_save_receiver, sender=Setting)


class JsCodeManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(status=True)

    def get_trusted_symbols(self):
        return self.get_queryset().filter(type="symbol", status=True)

    def get_header_tag_codes(self):
        return self.get_queryset().filter(location="header", type="tag", status=True)

    def get_footer_tag_codes(self):
        return self.get_queryset().filter(location="footer", type="tag", status=True)


class JsCode(models.Model):
    TYPE = (
        ('symbol', 'نماد'),
        ('tag', 'تگ'),
    )
    LOCATION = (
        ('header', 'هدر'),
        ('footer', 'فوتر'),
    )
    title = models.CharField(max_length=250, verbose_name="عنوان")
    slug = models.SlugField(null=True, verbose_name='نامک')
    code = models.TextField(blank=True, null=True, verbose_name="اسکریپت")
    type = models.CharField(max_length=50, blank=True, null=True, choices=TYPE, verbose_name='نوع')
    status = models.BooleanField(default=False, verbose_name='وضعیت')
    location = models.CharField(max_length=50, blank=True, null=True, choices=LOCATION, verbose_name='جانمایی کدک')
    location_order = models.IntegerField(default=1, verbose_name='ترتیب قرار گرفتن')
    objects = JsCodeManager()

    class Meta:
        verbose_name_plural = 'کدکها'
        verbose_name = 'کدک'

    def __str__(self):
        return self.title
