from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill
from extensions.utils import get_filename_ext


# Create your models here.

def upload_image_web_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"slides/web/{file_name}"


def upload_original_image_web_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"slides/web/{file_name}"


class Slider(models.Model):
    title = models.CharField(max_length=150, verbose_name='عنوان')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='عنوان slider در url')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    class Meta:
        verbose_name = 'اسلایدر'
        verbose_name_plural = 'اسلایدرها'

    def __str__(self):
        return self.title


class SliderSlideManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(is_active=True)


class SliderSlide(models.Model):
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    image_alt = models.CharField(max_length=250, null=True, verbose_name="متن جایگزین تصویر")
    image_tooltip = models.CharField(max_length=250, null=True, verbose_name="نام تصویر")
    link = models.URLField(max_length=250, null=True, blank=True, verbose_name="لینک صفحه فرود")
    original_image = ProcessedImageField(upload_to=upload_original_image_web_path, processors=[ResizeToFill(1600, 912)],
                                         options={'quality': 85}, verbose_name='لینک تصویر webp')
    image_webp = ProcessedImageField(upload_to=upload_image_web_path, blank=True, null=True,
                                     processors=[ResizeToFill(1600, 912)],
                                     format='WEBP', options={'quality': 85}, verbose_name='لینک تصویر webp')
    slider = models.ForeignKey(Slider, blank=True, on_delete=models.CASCADE, verbose_name='اسلایدر')
    is_origin_image = models.BooleanField(default=False, verbose_name='از تصویر اصلی استفاده شود')
    is_active = models.BooleanField(default=True, verbose_name='وضعیت')
    objects = SliderSlideManager()

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'اسلایدها'
        verbose_name = 'اسلاید'

    def __str__(self):
        return self.image_alt

    def save(self, *args, **kwargs):
        if not self._state.adding:
            old_image = self.__class__.objects.get(pk=self.pk).original_image
            if self.original_image != old_image:
                self.image_webp.delete()
                self.image_webp.save(self.original_image.name, self.original_image.file, save=False)
        else:
            self.image_webp.save(self.original_image.name, self.original_image.file, save=False)
        super().save(*args, **kwargs)
