from django.contrib import admin
from .models import Page, ContactUs, ContactSubject, Emails
import logging
# Register your models here.

class PageAdmin(admin.ModelAdmin):
    list_display = ['title','slug','update_at_ir','review_reason','url_tag']
    list_filter = ['status']
    exclude = ('created_at',)
    model = Page

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('user', 'status', 'review_reason',)
        return super(PageAdmin, self).add_view(request, form_url, extra_context)

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.status == 4 or obj.status == 3:
                if not (request.user.is_superuser or request.user.is_content_manager):
                    return False
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.user.is_superuser or request.user.is_content_manager:
            self.exclude = ('user',)
        else:
            self.exclude = ('user', 'status', 'review_reason',)
        return super(PageAdmin, self).change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_content_manager:
            return qs
        return qs.filter(user=request.user)

admin.site.register(Page,PageAdmin)


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['__str__','title__title']
    list_filter = ['status','title']

@admin.register(ContactSubject)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['__str__']


@admin.register(Emails)
class EmailsAdmin(admin.ModelAdmin):
    list_display = ['__str__']