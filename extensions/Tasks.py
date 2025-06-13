

from background_task import background

from extensions.seo import remove_link, create_link_in_content
from seo.models import JuiceLink
from settings.models import Setting

MS = Setting.objects.first()

PRODUCT_INTERNAL_LINK_TASK = 1000
if MS:
    PRODUCT_INTERNAL_LINK_TASK = MS.product_internal_link_task_run_time
POST_INTERNAL_LINK_TASK = 1000
if MS:
    POST_INTERNAL_LINK_TASK = MS.post_internal_link_task_run_time
CATEGORY_INTERNAL_LINK_TASK = 1000
if MS:
    CATEGORY_INTERNAL_LINK_TASK = MS.category_link_task_run_time
PAGE_INTERNAL_LINK_TASK = 1000
if MS:
    PAGE_INTERNAL_LINK_TASK = MS.page_internal_link_task_run_time

@background(schedule=PRODUCT_INTERNAL_LINK_TASK)
def create_product_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_products=True)
    from product.models import Product
    for product in Product.objects.filter(create_link_allowed=True, Description__isnull=False):
        html_content = remove_link(product.Description)
        for jlink in jlinks.filter(title__in=product.Description):
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
        for jlink in jlinks.filter(title__in=post.Description):
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
        for jlink in jlinks.filter(title__in=cat.description):
            authorized_tags_list = jlink.authorized_tags.split(",")
            cat.description = create_link_in_content(jlink.title, html_content, jlink.link,
                                                     authorized_tags_list)
            cat.save()
            html_content = cat.description

    create_category_internal_link()

@background(schedule=PAGE_INTERNAL_LINK_TASK)
def create_page_internal_link():
    jlinks = JuiceLink.objects.filter(apply_for_brands=True)
    from pages.models import Page
    for page in Page.objects.filter(create_link_allowed=True):
        html_content = remove_link(page.content)
        for jlink in jlinks.filter(title__in=page.content):
            authorized_tags_list = jlink.authorized_tags.split(",")
            page.content = create_link_in_content(jlink.title, html_content, jlink.link,
                                                  authorized_tags_list)
            page.save()
            html_content = page.content
    create_page_internal_link()