from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin

from .models import User


# Register your models here.
@admin.register(User)
class UaerAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display = ['__str__','is_superuser','is_active']
    list_filter = ['is_active']
    search_fields = ['email','first_name','last_name','mobile']
    filter_horizontal = ('user_permissions', 'groups',)
    exclude = ['password']
