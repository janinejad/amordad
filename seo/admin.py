from django.contrib import admin

from seo.models import JuiceLink


# Register your models here.

@admin.register(JuiceLink)
class JuiceLinkAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['__str__', 'link']
    search_fields = ['title', 'link']
    readonly_fields = ['get_cat_link_count', 'get_product_link_count', 'get_post_link_count',
                       'get_page_link_count']
