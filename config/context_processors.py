from django.core.cache import cache

from settings.models import Setting


def global_variable(request):
    st = cache.get('global_setting')

    if not st:
        st = Setting.objects.first()
        cache.set('global_setting', st, 60 * 5)  # کش برای ۵ دقیقه (300 ثانیه)

    return {
        'st': st
    }