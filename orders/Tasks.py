from datetime import datetime

from background_task import background
from django.utils import timezone

from extensions.seo import remove_link, create_link_in_content
from seo.models import JuiceLink
from settings.models import Setting

SETTING = Setting.objects.first()
cancel_time = 3600
if SETTING:
    cancel_time = SETTING.order_cancel_time


def subtract_from_stock(items):
    for item in items:
        item.variant.quantity -= item.product_count
        item.variant.save()


def add_to_stock(items):
    for item in items:
        item.variant.quantity += item.product_count
        item.variant.save()


@background(schedule=cancel_time)
def cancel_order(order_id):
    from orders.models import Order
    order = Order.objects.filter(id=order_id).first()
    if order:
        if not order.status_id in ['2', '3']:
            order.is_canceled = True
            order.save()
            add_to_stock(order.orderitem.all())

@background(schedule=1500)
def automatic_update():
    from product.models import Product,ProductInventory
    current_time = datetime.now()
    if current_time.hour == 11:
        products = Product.objects.all()
        for product in products:
            product.updated_at = timezone.now()
            product.save()
    automatic_update()

PRODUCT_INTERNAL_LINK_TASK = 1000
if SETTING:
    PRODUCT_INTERNAL_LINK_TASK = SETTING.product_internal_link_task_run_time
POST_INTERNAL_LINK_TASK = 1000
if SETTING:
    POST_INTERNAL_LINK_TASK = SETTING.post_internal_link_task_run_time
CATEGORY_INTERNAL_LINK_TASK = 1000
if SETTING:
    CATEGORY_INTERNAL_LINK_TASK = SETTING.category_link_task_run_time
PAGE_INTERNAL_LINK_TASK = 1000
if SETTING:
    PAGE_INTERNAL_LINK_TASK = SETTING.page_internal_link_task_run_time

@background(schedule=PRODUCT_INTERNAL_LINK_TASK)
def create_product_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_products=True)
    from product.models import Product
    for product in Product.objects.filter(create_link_allowed=True, Description__isnull=False):
        html_content = remove_link(product.Description)
        for jlink in jlinks:
            if jlink.title in product.Description:
                authorized_tags_list = jlink.authorized_tags.split(",")
                product.Description = create_link_in_content(jlink.title, html_content, jlink.link,
                                                             authorized_tags_list)
                product.save()
                html_content = product.Description
    create_product_internal_link()


@background(schedule=POST_INTERNAL_LINK_TASK)
def create_post_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_posts=True)
    from blog.models import Post
    for post in Post.objects.filter(create_link_allowed=True):
        html_content = remove_link(post.Description)
        for jlink in jlinks:
            if jlink.title in post.Description:
                authorized_tags_list = jlink.authorized_tags.split(",")
                post.Description = create_link_in_content(jlink.title, html_content, jlink.link,
                                                          authorized_tags_list)
                post.save()
                html_content = post.Description
    create_post_internal_link()


@background(schedule=CATEGORY_INTERNAL_LINK_TASK)
def create_category_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_categories=True)
    from product.models import ProductsCats
    for cat in ProductsCats.objects.filter(create_link_allowed=True):
        html_content = remove_link(cat.description)
        for jlink in jlinks:
            if jlink.title in cat.description:
                authorized_tags_list = jlink.authorized_tags.split(",")
                cat.description = create_link_in_content(jlink.title, html_content, jlink.link,
                                                         authorized_tags_list)
                cat.save()
                html_content = cat.description
    create_category_internal_link()

@background(schedule=PAGE_INTERNAL_LINK_TASK)
def create_page_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_pages=True)
    from pages.models import Page
    for page in Page.objects.filter(create_link_allowed=True):
        html_content = remove_link(page.content)
        for jlink in jlinks:
            if jlink.title in page.content:
                authorized_tags_list = jlink.authorized_tags.split(",")
                page.content = create_link_in_content(jlink.title, html_content, jlink.link,
                                                      authorized_tags_list)
                page.save()
                html_content = page.content

    create_page_internal_link()