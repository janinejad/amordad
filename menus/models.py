from django.db import models
from pages.models import Page
from django.forms import ValidationError
from product.models import ProductsCats
import math


class Menu(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان فهرست')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')

    class Meta:
        verbose_name_plural = 'فهرستهای فوتر'
        verbose_name = 'فهرست فوتر'

    def __str__(self):
        return self.title


class MenuList(models.Model):
    TYPE = (
        (2, 'نوشته ها'),
        (3, 'برگه ها'),
        (4, 'لینک دخواه'),
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, verbose_name='فهرست')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')
    url = models.URLField(verbose_name='ادرس صفحه', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'ایتمها'
        verbose_name = 'آیتم'

    def __str__(self):
        return self.title


class ProductCatMenuManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(is_active=True).order_by('display_order')


class ProductCatMenu(models.Model):
    TYPE = (
        (1, 'دسته بندی'),
        (3, 'تگ محصول'),
        (4, 'لینک دلخواه')
    )
    type = models.IntegerField(choices=TYPE, default=1, verbose_name='نوع لینک')
    title = models.CharField(max_length=250, verbose_name='عنوان')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')
    cat = models.ForeignKey(ProductsCats, on_delete=models.PROTECT, blank=True, null=True, verbose_name='دسته بندی')
    custom_link = models.URLField(blank=True, null=True, verbose_name='لینک دلخواه')
    parent_id = models.ForeignKey('ProductCatMenu', related_name='children', blank=True, null=True,
                                  on_delete=models.DO_NOTHING,
                                  verbose_name='دسته بندی مادر در منو')
    is_active = models.BooleanField(default=True, verbose_name='وضعیت')
    objects = ProductCatMenuManager()

    class Meta:
        verbose_name_plural = 'منوی دسته بندی کالا'
        verbose_name = 'آیتم های منو'

    def __str__(self):
        return self.title

    def has_children(self):
        children_count = self.children.count()
        if children_count > 0:
            return True
        else:
            return False

    def get_abs_url(self):
        if self.type == 1:
            return self.cat.get_abs_url()
        elif self.type == 4:
            return self.custom_link

    def clean(self):
        if self.type == 1:
            if not self.cat:
                raise ValidationError(
                    {'cat': 'دسته بندی را انتخاب نمایید.'})
        elif self.type == 4:
            if not self.custom_link:
                raise ValidationError(
                    {'custom_link': 'لینک دلخواه را وارد نمایید.'})
