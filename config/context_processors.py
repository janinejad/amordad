from settings.models import Setting


def global_variable(request):
    st: Setting = Setting.objects.first()
    return {
        'st': st
    }
