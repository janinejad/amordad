from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from jalali_date import datetime2jalali
from product.models import Product
from u_account.models import User

from tinymce.models import HTMLField


class Page(models.Model):
    STATUS = (
        (1, 'در انتظار بررسی'),
        (2, 'رفع ایراد'),
        (3, 'رد شده'),
        (4, 'تایید شده'),
    )
    status = models.IntegerField(choices=STATUS, default=1, verbose_name='وضعیت تایید')
    review_reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='علت عدم تایید')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ثبت کننده')
    title = models.CharField(max_length=250, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='نام در url')
    meta_desc = models.CharField(max_length=156, null=True, blank=True, verbose_name='توضیحات متا')
    meta_title = models.CharField(max_length=60, null=True, blank=True, verbose_name='عنوان سئو')
    keywords = models.CharField(max_length=150, verbose_name='کلمات کلیدی')
    # content = CKEditor5Field(blank=True, null=True, verbose_name='توضیحات اصلی')
    content = HTMLField(blank=True, null=True, verbose_name='توضیحات اصلی')
    content_jinja = models.TextField(null=True, blank=True, verbose_name='کدهای html پویا')
    use_content_jinja = models.BooleanField(default=False, verbose_name='استفاده از کدهای html پویا در صفحه')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روز رسانی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    create_link_allowed = models.BooleanField(default=False, verbose_name='وضعیت ساخت لینک داخلی')
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    is_main_page = models.BooleanField(default=False, verbose_name='محتوای صفحه اصلی سایت')


    class Meta:
        verbose_name_plural = 'برگه ها'
        verbose_name = 'برگه'

    def update_at_ir(self):
        jalalidate = datetime2jalali(self.updated_at).strftime('%Y/%m/%d در ساعت %H:%M')
        return jalalidate

    def __str__(self):
        return self.title

    def get_abs_url(self):
        return reverse('pages:page', kwargs={'slug': self.slug})

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    update_at_ir.short_description = "تاریخ به روزرسانی"

    def url_tag(self):
        return mark_safe(
            '<a href="{}" target="_blank">نمایش</a>'.format(reverse('pages:page', kwargs={'slug': self.slug})))

    url_tag.short_description = "لینک"


class ContactSubject(models.Model):
    title = models.CharField(max_length=250, verbose_name='عنوان')

    class Meta:
        verbose_name_plural = 'عناوین تماس با ما'
        verbose_name = 'عنوان تماس با ما'

    def __str__(self):
        return self.title


class ContactUs(models.Model):
    name = models.CharField(max_length=250, verbose_name=' نام و نام خانوادگی')
    phone_number = models.CharField(max_length=250, verbose_name='شماره تماس')
    email = models.EmailField(max_length=250, blank=True, null=True, verbose_name='آدرس ایمیل')
    title = models.ForeignKey(ContactSubject, on_delete=models.PROTECT, verbose_name='عنوان')
    text = models.TextField(max_length=1000, verbose_name='من درخواست')
    date = models.DateTimeField(auto_now=True, verbose_name='زمان ثبت تماس')
    status = models.BooleanField(default=False, verbose_name='وضعیت تماس')

    class Meta:
        verbose_name_plural = 'تماسها'
        verbose_name = 'تماس'

    def __str__(self):
        if self.name:
            return self.name
        else:
            return f"{self.id}"


class Emails(models.Model):
    email = models.EmailField(max_length=250,verbose_name='آدرس ایمیل')
    date = models.DateTimeField(auto_now=True, verbose_name='زمان ثبت تماس')

    class Meta:
        verbose_name_plural = 'ایمیلهای خبر نامه'
        verbose_name = 'ایمیل'

    def __str__(self):
        if self.email:
            return self.email
        return f"{self.id}"
