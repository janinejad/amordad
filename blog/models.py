import os

from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from jalali_date import datetime2jalali

from extensions.utils import get_filename_ext, unique_slug_generator
from django.db import models

from product.models import Product
# Create your models here.
from u_account.models import User


def upload_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{instance.id}-{timezone.now()}{ext}"
    return f"post/{file_name}"


class PostCategory(models.Model):
    title = models.CharField(max_length=250, verbose_name='عنوان')
    meta_title = models.CharField(blank=True, null=True, max_length=150, verbose_name='عنوان سئو')
    meta_description = models.TextField(blank=True, null=True, max_length=150, verbose_name='توضیحات سئو')
    keywords = models.TextField(max_length=150, blank=True, null=True, verbose_name='کلمات کلیدی')
    slug = models.SlugField(verbose_name='عنوان در url', unique=True)
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روز رسانی')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(1284, 600)],
                                format='WEBP', verbose_name='تصویر شاخص',
                                blank=True, null=True, help_text="طول 1284 و عرض 600 پیکسل باشد")
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')

    class Meta:
        verbose_name_plural = 'دسته بندی نوشته ها'
        verbose_name = 'دسته بندی نوشته'

    def __str__(self):
        return self.title

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def create_date_f(self):
        return f"{self.create_date.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def get_abs_url(self):
        return reverse("blog:blog", kwargs={'cat_slug': self.slug})

    def is_used(self):
        is_used = False
        if self.post_set.count() > 0:
            is_used = True
        return is_used


class Tag(models.Model):
    title = models.CharField(max_length=120, verbose_name='عنوان')
    slug = models.SlugField(verbose_name='عنوان در url', unique=True)
    timstamp = models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')
    active = models.BooleanField(default=True, verbose_name='وضعیت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روز رسانی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'برچسبها'
        verbose_name = 'برچسب'

    def is_used(self):
        is_used = False
        if self.post_set.count() > 0:
            is_used = True
        return is_used

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def get_abs_url(self):
        return reverse("blog:blog", kwargs={'tag_slug': self.slug})


def tag_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(tag_pre_save_receiver, sender=Tag)


class PostManger(models.Manager):
    def all(self):
        return self.get_queryset().filter(active=True)


class Post(models.Model):
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
    meta_title = models.CharField(blank=True, null=True, max_length=150, verbose_name='عنوان سئو')
    meta_desc = models.TextField(max_length=250, blank=True, null=True, verbose_name='توضیحات سئو')
    keywords = models.TextField(max_length=150, null=True, blank=True, verbose_name='کلمات کلیدی')
    slug = models.SlugField(unique=True, verbose_name='نام در url')
    Description = RichTextUploadingField(blank=True, null=True, verbose_name='توضیحات اصلی')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(1284, 600)],
                                format='WEBP', verbose_name='تصویر شاخص',
                                blank=True, null=True)
    thumb_image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(80, 80)],
                                      format='WEBP', verbose_name='تصویر بند انگشتی',
                                      blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='برچسبها')
    category = models.ForeignKey(PostCategory, on_delete=models.PROTECT, verbose_name='دسته بندی')
    date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روز رسانی')
    publish_at = models.DateTimeField(default=timezone.now, verbose_name='تاریخ انتشار')
    active = models.BooleanField(default=False, verbose_name='وضعیت')
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    create_link_allowed = models.BooleanField(default=True, verbose_name='وضعیت ساخت لینک داخلی')
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')
    objects = PostManger()

    class Meta:
        verbose_name_plural = 'نوشته ها'
        verbose_name = 'نوشته'
        ordering = ['-id']

    def get_thumb_image(self):
        if self.thumb_image:
            return self.thumb_image
        return self.image

    def __str__(self):
        return self.title

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def published_at_f(self):
        return f"{self.publish_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def updated_at_f_s(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}"

    def published_at_f_s(self):
        return f"{self.publish_at.strftime('%Y-%m-%dT%H:%M:%S')}"

    def user_has_comment(self, user):
        comments = self.comments_set.all().filter(user=user)
        if comments.count() > 5:
            return True
        else:
            return False

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        from django.templatetags.static import static
        return mark_safe('<img src="{}" height="50"/>'.format(static('img/admin/no-picture.png')))

    def post_date(self):
        jalalidate = datetime2jalali(self.date).strftime('%Y/%m/%d در ساعت %H:%M')
        return jalalidate

    def comment_counts(self):
        return self.comments_set.all().count()

    def get_abs_url(self):
        return reverse("blog:single_post", kwargs={'post_slug': self.slug})

    def url_tag(self):
        return mark_safe(
            '<a href="{}" target="_blank">نمایش</a>'.format(self.get_abs_url()))

    url_tag.short_description = "لینک"

    image_tag.short_description = "تصویر"


class CommentManagement(models.Manager):
    def all(self):
        return self.get_queryset().filter(is_confirmed=True)


class Comments(models.Model):
    POST_TYPE = (
        ('2', 'نوشته ها'),
        ('3', 'محصولات'),
    )
    comment = models.TextField(max_length=500, verbose_name='متن نظرسنجی')
    post_type = models.CharField(max_length=2, choices=POST_TYPE, verbose_name='نوع پست')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, verbose_name='عنوان پست')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, verbose_name='عنوان محصول')
    date = models.DateTimeField(auto_now_add=timezone.now, verbose_name='تاریخ نظرسنجی')
    is_confirmed = models.BooleanField(default=False, verbose_name='وضعیت تایید')
    name = models.CharField(max_length=250,verbose_name='نام و نام خانوادگی')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='عنوان کاربر')
    objects = CommentManagement()

    class Meta:
        verbose_name_plural = 'نظرات در مورد پست ها'
        verbose_name = 'نظر در مورد پست'
        ordering = ['-id']

    def __str__(self):
        if self.name:
            return self.name
        return f"ناشناس {self.id}"

    def comment_date(self):
        jalalidate = datetime2jalali(self.date).strftime('%Y/%m/%d در ساعت %H:%M')
        return jalalidate

    def get_user_full_name(self):
        return self.user.get_full_name()
    def get_image_url(self):
        if self.user:
            if self.user.image:
                return self.user.image.url
        from django.templatetags.static import static
        return static('img/avatars/02.png')



class CommentReply(models.Model):
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, null=True, blank=True, verbose_name='پاسخ')
    text = models.TextField(max_length=500, verbose_name='متن پاسخ')
    date = models.DateTimeField(auto_now_add=timezone.now, verbose_name='تاریخ نظرسنجی')

    class Meta:
        verbose_name_plural = 'پاسخ ها'
        verbose_name = 'پاسخ'
        ordering = ['-id']

    def comment_date(self):
        jalalidate = datetime2jalali(self.date).strftime('%Y/%m/%d در ساعت %H:%M')
        return jalalidate
