from django.contrib import admin
from .models import Financials, SMSSetting, Setting, CompanyInfo, JsCode


# Register your models here.

@admin.register(Financials)
class FinancialsAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    def has_add_permission(self, request):
        setting_count = Financials.objects.all().count()
        if setting_count > 0:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        setting_count = CompanyInfo.objects.all().count()
        if setting_count > 0:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SMSSetting)
class SMSSettingAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        setting_count = SMSSetting.objects.all().count()
        if setting_count > 0:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Setting)
class SMSSettingAdmin(admin.ModelAdmin):
    list_display = ["__str__"]

    def has_add_permission(self, request):
        setting_count = Setting.objects.all().count()
        if setting_count > 0:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(JsCode)
class JsCodeAdmin(admin.ModelAdmin):
    list_display = ['__str__','type','location','location_order','status']
    list_filter = ['location','status']
    list_editable = ['location_order','status']

    class Meta:
        model = JsCode