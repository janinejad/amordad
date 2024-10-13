from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from imagekit.models.fields import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.utils import timezone
from django.core.validators import RegexValidator
from extensions.utils import get_filename_ext
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from social_django.models import UserSocialAuth
from django.core.validators import EmailValidator


# Create your models here.
def upload_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    file_name = f"{timezone.now()}{ext}"
    return f"profile/{file_name}"


class User(AbstractUser):
    mobile = models.CharField(max_length=11, blank=True, null=True, verbose_name="شماره موبایل", unique=True,
                              validators=[RegexValidator(regex='^09\d{9}$',
                                                         message='فرمت شماره موبایل اشتباه است.')])
    image = ProcessedImageField(upload_to=upload_image_path, processors=[ResizeToFill(64, 64)],
                                format='JPEG', options={'quality': 100}, verbose_name='تصویر کاربر',
                                blank=True, null=True)
    otp = models.PositiveIntegerField(blank=True, null=True, verbose_name="کد احراز هویت")
    email = models.EmailField(validators=[EmailValidator(message='یک آدرس ایمیل معتبر وارد نمایید.')],
                              verbose_name='آدرس ایمیل')
    email_active_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='کد فعالسازی ایمیل')
    otp_create_time = models.DateTimeField(auto_now=True)
    tel_no = models.CharField(max_length=12, null=True, blank=True, verbose_name="شماره تلفن")
    send_news = models.BooleanField(default=True, verbose_name='دریافت خبر نامه')
    personal_address = models.CharField(null=True, blank=True,max_length=1000, verbose_name='آدرس منزل')
    is_official = models.BooleanField(default=False,verbose_name='کاربر شخصیت حقوقی است')
    has_order_invoice = models.BooleanField(default=False,verbose_name='نمایش فاکتور مشتریان')
    organization_name = models.CharField(max_length=60, null=True, blank=True, verbose_name='نام سازمان')
    firm_national_id = models.CharField(max_length=11, null=True, blank=True, verbose_name='شناسه ملی شرکت')
    firm_economical_no = models.CharField(max_length=11, null=True, blank=True, verbose_name='شناسه ملی شرکت')
    firm_no = models.CharField(max_length=150, null=True, blank=True, verbose_name='شماره ثبت')
    official_postal_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='کد پستی')
    official_address = models.CharField(null=True, blank=True,max_length=1000, verbose_name='آدرس حقوقی')
    firm_tel_no = models.CharField(max_length=12, null=True, blank=True, verbose_name="شماره تماس حقوقی")

    class Meta:
        ordering = ['id']
        verbose_name = 'حساب کاربر'
        verbose_name_plural = 'حساب کاربران'

    def __str__(self):
        if self.first_name and self.last_name:
            return self.get_full_name()
        else:
            return self.email


@receiver(pre_save, sender=UserSocialAuth)
def user_social_auth_pre_save_function(sender, instance, **kwargs):
    lookup = ~Q(id=instance.user.id) & Q(email=instance.uid)
    user = User.objects.filter(lookup).first()
    user_to_delete_id = instance.user.id
    user_to_delete = User.objects.filter(id=user_to_delete_id).first()
    if user:
        instance.user = user
        if user_to_delete:
            user_to_delete.delete()
