from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from blog.models import Post
from pages.forms import ContactUsForm, SendEmailForm
from pages.models import Page, Emails
from django.http import Http404, HttpResponseGone, HttpRequest, JsonResponse

from settings.models import Setting


# Create your views here.


def page(request, *args, **kwargs):
    slug = kwargs['slug']
    page = cache.get(f"page_{slug}")
    if not page:
        page = Page.objects.filter(slug=slug).first()
        cache.set(f"page_{slug}", page, 60 * 5)

    posts = cache.get('posts')
    if not posts:
        posts = Post.objects.all().order_by('-id')[:3]
        cache.set('posts', posts, 60 * 5)

    if page is None:
        raise Http404("صفحه مورد نظر یافت نشد")
    if page.http_response_gone:
        return HttpResponseGone("این صفحه دیگر وجود ندارد.")
    context = {
        'page': page,
        'posts': posts,
    }
    return render(request, 'page.html', context)


class ContactUsView(View):
    def get(self, request: HttpRequest):
        form = ContactUsForm()
        context = {
            'form': form,
        }
        return render(request, 'contact_us.html', context)

    def post(self, request: HttpRequest):
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'تبریک! پیام شما با موفقیت ثبت گردید.کارشناسان ما به زودی با شما تماس خواهند گرفت.')
            return redirect(reverse('home'))
        context = {
            'form': form,
        }
        return render(request, 'contact_us.html', context)


def send_email_address(request):
    form = SendEmailForm(request.POST or None)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        if form.is_valid():
            email = Emails.objects.filter(email=request.POST.get('email')).first()
            if email:
                messages.success(request,
                                 'شما قبلا عضو خبر نامه شده است!')
                return JsonResponse({}, status=200)
            form.save()
            messages.success(request,
                             'تبریک! آدرس ایمیل شما با موفقیت ارسال گردید.')
            form = SendEmailForm()
            return JsonResponse({}, status=200)

        return JsonResponse({}, status=401)
    context = {
        'form': form,
    }
    return render(request, 'email-address.html', context)
