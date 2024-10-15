from django.shortcuts import render
from .models import Slider


# Create your views here.
def get_slider(request, *args, slug=None, **kwargs):
    slider = Slider.objects.filter(slug=slug).first()
    slides = []
    if slider:
        slides = slider.sliderslide_set.all()
    context = {
        'slides': slides,
    }
    return render(request, "Shared/_Slider.html", context)