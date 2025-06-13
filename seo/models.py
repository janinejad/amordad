from django.db import models

from blog.models import Post
from pages.models import Page
from product.models import Product, ProductsCats, Brand


# Create your models here.


class JuiceLinkManager(models.Manager):
    def all_sorted_by_prirority(self):
        return self.get_queryset().order_by('prirority')


class JuiceLink(models.Model):
    title = models.CharField(max_length=256, verbose_name='کلمه کلیدی')
    link = models.URLField(max_length=2000, verbose_name='لینک')
    prirority = models.IntegerField(default=0, verbose_name='اولویت')
    authorized_tags = models.TextField(verbose_name='تگهایی مجاز', help_text='تگها را با , از همدیگر جدا کنید')
    apply_for_posts = models.BooleanField(default=False, verbose_name='برای نوشته ها اعمال گردد')
    apply_for_products = models.BooleanField(default=False, verbose_name='برای توضیحات محصولات اعمال گردد')
    apply_for_pages = models.BooleanField(default=False, verbose_name='برای صفحه هات اعمال گردد')
    apply_for_categories = models.BooleanField(default=False, verbose_name='برای دسته بندی محصولات اعمال گردد')
    objects = JuiceLinkManager()

    class Meta:
        ordering = ['prirority']
        verbose_name_plural = "لینکهای داخلی"
        verbose_name = "لینک داخلی"

    def __str__(self):
        return self.title

    def get_page_link_count(self):
        pages = Page.objects.filter(content__icontains=self.title)
        return pages.count()

    def get_post_link_count(self):
        posts = Post.objects.filter(Description__icontains=self.title)
        return posts.count()

    def get_product_link_count(self):
        products = Product.objects.filter(Description__icontains=self.title)
        return products.count()

    def get_cat_link_count(self):
        cats = ProductsCats.objects.filter(description__icontains=self.title)
        return cats.count()

    get_page_link_count.short_description = 'تعداد لینک در صفحه هات'
    get_cat_link_count.short_description = 'تعداد لینک در دسته بندی'
    get_product_link_count.short_description = 'تعداد لینک در مجصولات'
    get_post_link_count.short_description = 'تعداد لینک در نوشته ها'
