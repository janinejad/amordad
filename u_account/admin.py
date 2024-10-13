from django.contrib import admin
from .models import User


# Register your models here.
@admin.register(User)
class UaerAdmin(admin.ModelAdmin):
    list_display = ['__str__','is_superuser','is_active']
    list_filter = ['is_active']
