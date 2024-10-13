from django.urls import path, include
from .views import get_slider

app_name = 'components'
urlpatterns = [
    path('slider/<slug>', get_slider, name='slider'),
]
