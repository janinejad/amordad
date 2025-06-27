import math
import os
from datetime import datetime
from django.db import models
from django.db.models import Q, Min
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ProcessedImageField
from jalali_date import datetime2jalali
from pilkit.processors import ResizeToFill
from extensions.utils import unique_slug_generator
from u_account.models import User


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"products/{datetime.today().year}/{datetime.today().month}/{file_name}"


def upload_image_path_200(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"products/s200/{datetime.today().year}/{datetime.today().month}/{file_name}"


def upload_image_path_300(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"products/s300/{datetime.today().year}/{datetime.today().month}/{file_name}"


def upload_image_path_500(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"products/s500/{datetime.today().year}/{datetime.today().month}/{file_name}"


def upload_thumbnail_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"products_thumbnail/{file_name}"


def upload_image_path_brand(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"brands/{file_name}"


# Create your models here.
class Brand(models.Model):
    review_reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='علت عدم تایید')
    meta_title = models.CharField(blank=True, null=True, max_length=250, verbose_name='عنوان سئو')
    meta_description = models.TextField(blank=True, max_length=500, null=True, verbose_name='توضیحات متا')
    meta_keywords = models.TextField(blank=True, max_length=250, null=True, verbose_name='کلمات کلیدی')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ثبت کننده')
    title = models.CharField(max_length=150, verbose_name='عنوان برند')
    display_order = models.IntegerField(default=2, verbose_name='اولویت نمایش')
    image = ProcessedImageField(upload_to=upload_image_path_brand, processors=[ResizeToFill(148, 148)],
                                format='WEBP', verbose_name='تصویر شاخص',
                                blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(default=True, verbose_name='وضعیت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به روز رسانی")
    shortDescription = CKEditor5Field(blank=True, null=True, verbose_name='توضیحات کوتاه')
    Description = CKEditor5Field(blank=True, null=True, verbose_name='توضیحات اصلی')
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    create_link_allowed = models.BooleanField(default=False, verbose_name='وضعیت ساخت لینک داخلی')
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')

    class Meta:
        verbose_name_plural = 'برندها'
        verbose_name = 'برند'
        ordering = ['display_order']

    def __str__(self):
        return self.title

    def get_breadcrumb(self):
        breadcrumb = f"<a href='#' class='jimbo-orange-bold'>{self.title}</a>"
        return breadcrumb

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        return ""

    def get_abs_url(self):
        return reverse('j_products:brand', kwargs={'slug': self.slug})

    def get_p_abs_url(self):
        # return reverse("j_filtering:products-search", kwargs={'brand': self.slug})
        return "در حال انجام"

    image_tag.short_description = "تصویر برند"

    def url_tag(self):
        # return mark_safe(
        #     '<a href="{}" target="_blank">نمایش</a>'.format(
        #         reverse('j_filtering:products-search', kwargs={'brand': self.slug})))
        return "در حال انجام"

    url_tag.short_description = "لینک"


def brand_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(brand_pre_save_receiver, sender=Brand)


class ProductExperts(models.Model):
    name = models.CharField(max_length=150, verbose_name='نام و نام خانوادگی')
    position = models.CharField(max_length=150, verbose_name='سمت')
    whatsapp_number = models.CharField(max_length=11, verbose_name='شماره واتس اپ')
    phone_number = models.CharField(max_length=50, verbose_name='شماره تماس')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(520, 290)],
                                format='JPEG', options={'quality': 85}, verbose_name='تصویر کارشناس')

    class Meta:
        verbose_name_plural = 'کارشناسان محصول'
        verbose_name = 'کارشناس محصول'

    def __str__(self):
        return self.name


class ProductCatsManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(is_active=True)

    def get_slider_cats(self):
        return self.all().filter(for_display_in_slider=True)


class ProductsCats(models.Model):
    title = models.CharField(max_length=150, verbose_name='عنوان')
    meta_title = models.CharField(blank=True, null=True, max_length=250, verbose_name='عنوان سئو')
    meta_description = models.TextField(blank=True, null=True, max_length=500, verbose_name='توضیحات سئو')
    keywords = models.TextField(max_length=250, null=True, blank=True, verbose_name='کلمات کلیدی')
    description = CKEditor5Field(blank=True, null=True, verbose_name='توضیحات')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(1120, 630)],
                                format='WEBP', verbose_name='تصویر شاخص',
                                blank=True, null=True)
    slug = models.SlugField(max_length=150, unique=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(default=False, verbose_name='وضعیت')
    for_display_in_slider = models.BooleanField(default=False, verbose_name='نمایش در اسلایدر دسته بندی ها')
    parent_id = models.ForeignKey('ProductsCats', null=True, blank=True, related_name='children',
                                  on_delete=models.DO_NOTHING,
                                  verbose_name='دسته بندی مادر')
    experts = models.ManyToManyField(ProductExperts, verbose_name='کارشناسان این دسته بندی')
    depth = models.IntegerField(verbose_name='عمق گروه', default=1, null=True)
    Display_order = models.IntegerField(verbose_name='ترتیب نمایش', default=1)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روز رسانی')
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    create_link_allowed = models.BooleanField(default=False, verbose_name='وضعیت ساخت لینک داخلی')
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')
    objects = ProductCatsManager()

    class Meta:
        verbose_name_plural = 'دسته بندی محصولات'
        verbose_name = 'دسته بندی'
        ordering = ['Display_order']

    def __str__(self):
        return self.title

    def get_breadcrumb(self):
        breadcrumb = ""
        current_category = self
        count = 0
        while current_category.parent_id:
            count += 1
            tag = ""
            if current_category == self:
                tag = f"<a href='#' class='jimbo-orange-bold'>{current_category.title}</a>"
            else:
                tag = f"<a href='{current_category.get_abs_url()}'>{current_category.title}</a>"
            breadcrumb = tag + breadcrumb
            current_category = current_category.parent_id
        if not current_category.parent_id:
            if count > 0:
                tag = f"<a href='{current_category.get_abs_url()}'>{current_category.title}</a>"
            else:
                tag = f"<a href='#' class='jimbo-orange-bold'>{current_category.title}</a>"
            breadcrumb = tag + breadcrumb
        return breadcrumb

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def get_abs_url(self):
        return reverse("products:product_category", kwargs={'cat_s': self.slug})

    def get_image(self):
        if self.image:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        from django.templatetags.static import static
        return mark_safe('<img src="{}" height="50"/>'.format(static('img/admin/no-picture.png')))

    def get_products_count(self):
        count = 0
        for l1 in self.children.all():
            count = count + l1.product_set.count()
            if l1.children.count() > 0:
                for l2 in l1.children.all():
                    count = count + l2.product_set.count()
                    if l2.children.count() > 0:
                        for l3 in l2.children.all():
                            count = count + l3.product_set.count()
        return count

    get_image.short_description = "تصویر"

    def has_products(self):
        if self.product_set.all().count() > 0:
            return True
        else:
            return False

    def middle_cat(self):
        if self.parent_id and not (self.parent_id.parent_id):
            return True
        else:
            return False

    def url_tag(self):
        return mark_safe(
            '<a href="{}" target="_blank">نمایش</a>'.format(
                reverse("products:product_category", kwargs={'cat_s': self.slug})))

    url_tag.short_description = "لینک"
    is_active.short_description = "وضعیت"
    has_products.short_description = "دارای محصول"
    middle_cat.short_description = "دسته بندی میانی"
    has_products.boolean = True
    middle_cat.boolean = True
    is_active.boolean = True


def products_cats_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(products_cats_pre_save_receiver, sender=ProductsCats)


def products_cats_post_save_receiver(sender, instance, *args, **kwargs):
    if not instance.parent_id:
        instance.depth = 1
    else:
        instance.depth = instance.parent_id.depth + 1


post_save.connect(products_cats_post_save_receiver, sender=ProductsCats)


class ProductManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(active=True)

    def get_product_by_id(self, id, is_staff=False):
        try:
            if is_staff:
                qs = self.get_queryset().get(id=id)
            else:
                qs = self.get_queryset().get(id=id, active=True)
            return qs
        except self.model.DoesNotExist:
            return None

    def search(self, query):
        lookup = models.Q(title__icontains=query) | models.Q(Description__icontains=query)
        return self.get_queryset().filter(lookup, active=True).distinct()

    def get_available_products(self):
        return self.get_queryset().all().filter(productinventory__quantity__gt=0,
                                                productinventory__price__gt=0).distinct()

    def newest_products(self):
        return self.get_available_products().order_by('-id')


class Units(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name='عنوان')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'واحد اندازه گیری'
        verbose_name_plural = 'واحد های اندازه گیری'


class Product(models.Model):
    title = models.CharField(max_length=600, verbose_name='عنوان',
                             help_text='این فیلد نباید خالی باشد و تعداد کارکترهای آن باید بیشتر از 150 کاراکتر نباشند')
    en_title = models.CharField(max_length=600, verbose_name='نام انگلیسی محصول', blank=True, null=True)
    unit = models.ForeignKey(Units, on_delete=models.PROTECT, verbose_name='واحد اندازه گیری')
    meta_title = models.CharField(max_length=600, null=True, blank=True, verbose_name='عنوان سئو')
    meta_desc = models.CharField(max_length=600, null=True, blank=True, verbose_name='توضیحات سئو')
    keywords = models.TextField(max_length=600, null=True, blank=True, verbose_name='کلمات کلیدی')
    slug = models.SlugField(unique=True, blank=True, verbose_name='نام در url')
    Description = CKEditor5Field(blank=True, null=True, verbose_name='توضیحات اصلی')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ثبت کننده')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(1120, 630)],
                                format='WEBP', verbose_name='تصویر شاخص',
                                blank=True, null=True)
    image_alt = models.CharField(max_length=500, null=True, blank=True, verbose_name='عنوان تصویر')
    active = models.BooleanField(default=False, verbose_name='وضعیت')
    RootCategoryId = models.ForeignKey(ProductsCats, on_delete=models.SET_NULL, null=True,
                                       verbose_name='دسته بندی')
    brandId = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True,
                                verbose_name='برند')
    dkp_name = models.CharField(max_length=150, null=True, blank=True, verbose_name='سناسه محصول')
    similar_products = models.ManyToManyField('Product', blank=True, verbose_name='محصولات مشابه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به روز رسانی')
    video_link = models.URLField(null=True, blank=True, verbose_name='لینک ویدئوی محصول')
    review_reason = models.CharField(max_length=250, null=True, blank=True, verbose_name='علت عدم تایید')
    canonical = models.URLField(verbose_name='لینک کنونیکال', null=True, blank=True)
    create_link_allowed = models.BooleanField(default=False, verbose_name='وضعیت ساخت لینک داخلی')
    is_noindex = models.BooleanField(default=False, verbose_name='صفحه noindex شود')
    http_response_gone = models.BooleanField(default=False, verbose_name='410 شود')
    objects = ProductManager()

    class Meta:
        verbose_name_plural = 'محصولات'
        verbose_name = 'محصول'

    def get_price(self):
        price = 0
        lowest_price = self.productinventory_set.aggregate(min_value=Min('price'))['min_value']
        if lowest_price:
            price = lowest_price
        return '{:,} تومان'.format(math.trunc(price))

    def updated_at_f(self):
        return f"{self.updated_at.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"

    def update_at_ir(self):
        jalalidate = datetime2jalali(self.updated_at).strftime('%Y/%m/%d در ساعت %H:%M')
        return jalalidate

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        from django.templatetags.static import static
        return mark_safe('<img src="{}" height="50"/>'.format(static('img/admin/no-picture.png')))

    def get_user_full_name(self):
        if self.user:
            return self.user.full_name()
        else:
            return "بدون کاربر"

    image_tag.short_description = "تصویر"
    get_user_full_name.short_description = "ثبت کننده"

    def __str__(self):
        return self.title

    def get_product_attr(self):
        product_attrs = []
        attrs = Attribute.objects.filter(attributeitem__productattribute__products=self).distinct()
        for a in attrs:
            items = ProductAttribute.objects.filter(attributeItem__attribute=a, products=self).distinct()
            obj = {'attr': a, 'items': items}
            product_attrs.append(obj)
        return product_attrs

    def get_abs_url(self):
        return reverse("products:product", kwargs={'id': self.id})

    def get_price_valid_until(self):
        from datetime import datetime, timedelta
        current_date = datetime.now().date()
        tomorrow_date = current_date + timedelta(days=1)
        return tomorrow_date.strftime("%Y-%m-%d")

    def get_url_name(self):
        return self.title.replace(' ', '-').replace('/', '-')

    def get_full_abs_url(self):
        return reverse("products:product",
                       kwargs={'id': self.id, 'product_name': self.title.replace(' ', '-').replace('/', '-')})

    def url_tag(self):
        return mark_safe(
            '<a href="{}" target="_blank">نمایش</a>'.format(self.get_full_abs_url()))

    url_tag.short_description = "لینک"

    def get_related_products(self):
        lookup = models.Q(id=self.RootCategoryId.id) | models.Q(id__in=self.otherCategories.all())
        cats = ProductsCats.objects.filter(lookup)
        return Product.objects.filter(RootCategoryId__in=cats)

    def get_default_variant(self):
        variant = self.productinventory_set.filter(regular_price__gt=0, status=True, quantity__gt=0).order_by(
            'price').distinct().first()
        return variant

    def get_full_sharing_url(self):
        from settings.models import Setting
        return f"{Setting.objects.first().siteUrl}{reverse('products:product', kwargs={'id': self.id, 'product_name': self.title.replace(' ', '-').replace('/', '-')})}"

    def is_available(self):
        if self.get_default_variant():
            return True
        else:
            return False


class ProductGallery(models.Model):
    title = models.CharField(max_length=150, verbose_name='عنوان')
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(1120, 630)],
                                format='WEBP', options={'quality': 85}, verbose_name='لینک تصویر jpeg',
                                blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='عنوان محصول')

    class Meta:
        verbose_name_plural = 'تصاویر محصول'
        verbose_name = 'تصویر محصول'

    def __str__(self):
        return self.title

    def get_id(self):
        return self.id

    get_id.short_description = 'شناسه تصویر'


class ProductInventoryManager(models.Manager):
    def all_availble(self):
        return self.get_queryset().filter(quantity__gt=0, in_basket__gt=0).order_by('price').distinct()
    def all(self):
        return self.get_queryset().order_by('-quantity').distinct()


class ProductInventory(models.Model):
    title = models.CharField(max_length=150, null=True, blank=True, verbose_name='عنوان')
    products = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    weight = models.IntegerField(default=0, verbose_name='وزن')
    thickness = models.FloatField(default=0, verbose_name='ضخامت')
    quantity = models.IntegerField(default=0, verbose_name='موجودی')
    in_basket = models.IntegerField(default=1, verbose_name='محدودیت تعداد در سبد')
    delivery_time = models.PositiveSmallIntegerField(default=1, verbose_name='زمان تحویل این محصول(روز)')
    unit = models.FloatField(default=0, verbose_name='هر واحد برابر است با')
    supplement_price = models.FloatField(default=0, verbose_name='قیمت تامین')
    regular_price = models.FloatField(default=0, verbose_name='قیمت عادی')
    after_discount = models.FloatField(default=0, verbose_name='قیمت بعد از کسر تخفیف')
    price = models.FloatField(default=0, verbose_name='قیمت اعمال شده')
    status = models.BooleanField(default=True, verbose_name='وضعیت نمایش')
    on_sale_from = models.DateTimeField(default=timezone.now, null=True, verbose_name='ویژه از تاریخ')
    on_sale_to = models.DateTimeField(default=timezone.now, null=True, verbose_name='ویژه تا تاریخ')
    objects = ProductInventoryManager()

    def __str__(self):
        return f"{self.products}"

    def product_amount_with_tax_ir(self):
        from settings.models import Financials
        st = Financials.objects.first()
        tax = 0
        if st:
            tax = st.tax
        return '{:,} تومان'.format(math.trunc((tax / 100 * self.price) + self.price))

    def variant_name(self):
        return f"{self.weight} - {self.products.unit}"

    class Meta:
        verbose_name_plural = "تنوع های محصول"
        verbose_name = "تنوع محصول"
        ordering = ['thickness']

    def regular_price_ir(self):
        return '{:,} تومان'.format(math.trunc(self.regular_price))

    def price_ir(self):
        return '{:,} تومان'.format(math.trunc(self.price))

    def get_weight_ir(self):
        return '{:,} کیلوگرم'.format(math.trunc(self.weight))

    def dynamic_name(self):
        name = ''
        if not self.title:
            name = self.products
        else:
            name = self.title
        return name
    def variant_is_availble(self):
        if self.quantity > 0:
            return True
        else:
            return False


def product_inventory_pre_post_save_receiver(sender, instance, *args, **kwargs):
    if instance.after_discount > 0 and instance.regular_price > instance.after_discount and instance.on_sale_from <= timezone.now() <= instance.on_sale_to:
        instance.price = instance.after_discount
    else:
        instance.price = instance.regular_price


pre_save.connect(product_inventory_pre_post_save_receiver, sender=ProductInventory)


class ProductFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "محصولات پسند شده"
        verbose_name = "محصول پسند شده"

    def __str__(self):
        return f"{self.product} - {self.user.get_full_name()}"


class ProductMainFeature(models.Model):
    feature = models.CharField(max_length=150, verbose_name='مشخصه')
    feature_value = models.CharField(max_length=150, verbose_name='مقدار')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='عنوان محصول')

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'مشخصات اصلی محصول'
        verbose_name = 'مشخصه اصلی'

    def __str__(self):
        return self.feature


class GroupAttribute(models.Model):
    title = models.CharField(max_length=250, blank=False, verbose_name="عنوان گروه")
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')

    class Meta:
        verbose_name = "گروه ویژگی"
        verbose_name_plural = "گروه های ویژگی"

    def __str__(self):
        return self.title


class Attribute(models.Model):
    title = models.CharField(max_length=250, blank=False, verbose_name="عنوان")
    group_attribute = models.ForeignKey(GroupAttribute, on_delete=models.PROTECT, verbose_name='گروه ویژگی')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگیها"

    def __str__(self):
        return self.title

    def is_color(self):
        if self.type == 3:
            return True
        else:
            return False

    is_color.boolean = True


class AttributeItemManager(models.Manager):
    def get_all_assign(self):
        lookup = ~Q(productattribute__products=None)
        return self.get_queryset().filter(lookup, productattribute__products__active=True).distinct().order_by('item')


class AttributeItem(models.Model):
    item = models.TextField(verbose_name='مقدار')
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, verbose_name='ویژگی')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True, verbose_name='تصویر')
    objects = AttributeItemManager()

    class Meta:
        verbose_name_plural = 'مقادیر ویژگیها'
        verbose_name = 'مقدارویژگی'

    def __str__(self):
        return f"{self.id} - {self.attribute.group_attribute} - {self.attribute} - {self.item}"


class ProductAttributeManager(models.Manager):
    def all(self):
        return self.get_queryset().order_by('id')


class ProductAttribute(models.Model):
    attributeItem = models.ForeignKey(AttributeItem, on_delete=models.PROTECT, verbose_name='مقدار ویژگی')
    products = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    display_order = models.IntegerField(default=1, verbose_name='اولویت نمایش')
    objects = ProductAttributeManager()

    def __str__(self):
        return f"{self.attributeItem.attribute.title} - {self.attributeItem.item}"

    def attr(self):
        return self.attributeItem.item

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'ویژگی های محصول'
        verbose_name = 'ویژگی محصول'


class AttributeFilter(models.Model):
    title = models.CharField(max_length=150, verbose_name='عنوان فیلتر')
    category = models.ForeignKey(ProductsCats, on_delete=models.CASCADE, verbose_name='دسته بندی')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name='ویژگی')
    display_order = models.IntegerField(default=1, verbose_name='الویت نمایش')

    class Meta:
        verbose_name_plural = 'فیلترهای دسته بندی'
        verbose_name = 'فیلتر دسته بندی'

    def __str__(self):
        return self.title
