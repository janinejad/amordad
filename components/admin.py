from django.contrib import admin
from .models import Slider, SliderSlide
import admin_thumbnails
from django.forms import TextInput, URLInput, FileInput
from django.db import models
# Register your models here.

@admin_thumbnails.thumbnail('original_image', alias='تصویر')
class SliderSlideInLine(admin.TabularInline):
    model = SliderSlide
    exclude = ['image_webp']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '8'})},
        models.URLField: {'widget': URLInput(attrs={'size': '8'})},
        models.ImageField: {'widget': FileInput(attrs={'size': '8'})},
    }
    extra = 0


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    inlines = [SliderSlideInLine]
