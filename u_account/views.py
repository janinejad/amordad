from cryptography.hazmat.backends.openssl import backend
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponse, Http404, HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.contrib import messages
from django.views.generic import DetailView
from weasyprint import HTML

from orders.models import Order
from settings.models import CompanyInfo, Financials
from u_account.forms import RegisterForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, EditInfoForm
from u_account.models import User
from django.contrib.auth import login, logout

from utils.email_service import send_email_to_user


# Create your views here.


def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = RegisterForm(request.POST or None)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            from django.utils import timezone
            instance.email_active_code = get_random_string(72)
            instance.set_password(instance.password)
            instance.username = instance.email
            instance.save()
            user = User.objects.filter(id=instance.id).first()
            send_email_to_user('فعالسازی حساب کاربری', user.email, {'user': user}, 'emails/activate_account.html')
            messages.success(request,
                             'ثبت نام با موفقیت انجام شد. جهت فعال سازی حساب خود بر روی لینک فعال سازی ارسال شده به ایمیلتان مراجعه نمایید.')
            return JsonResponse({}, status=200)
        else:
            return JsonResponse(get_errors(form), status=401)


def login_m(request):
    if request.user.is_authenticated:
        return redirect('/')
    form = LoginForm(request.POST)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == "POST":
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            user_pass = form.cleaned_data.get('password')
            user = User.objects.filter(email__iexact=user_email).first()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            if user is not None:
                if not user.is_active:
                    form.add_error('email',
                                   'حساب کاربری شما فعال نشده است.جهت فعال سازی به ایمیل خود مراجه نمایید و روی لینک فعال سازی ارسال شده کلیک نمایید.')
                    return JsonResponse(get_errors(form), status=401)
                else:
                    is_password_correct = user.check_password(user_pass)
                    if is_password_correct:
                        login(request, user)
                        messages.success(request,
                                         'تبریک! شما با موفقیت وارد حساب کاربری خود شدید.')
                        return JsonResponse({}, status=200)
                    else:
                        form.add_error('email', 'نام کاربری یا رمز عبور اشتباه است.')
                        return JsonResponse(get_errors(form), status=401)
            else:
                form.add_error('email', 'کاربری با مشخصات وارد شده یافت نشد')
            return JsonResponse(get_errors(form), status=401)
        else:
            return JsonResponse(get_errors(form), status=401)


class ActivateAccountView(View):
    def get(self, request, activation_code=None):
        if not activation_code:
            if request.user.is_authenticated:
                return render(request, 'activate_account.html', {})
            else:
                return redirect(reverse('home'))

        user: User = User.objects.filter(email_active_code__iexact=activation_code).first()
        if user is not None:
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(72)
                user.save()
                if request.user.is_authenticated:
                    messages.success(request,
                                     'تبریک! حساب شما با موفقیت فعال گردید.')
                    return redirect(reverse('account:activate_account'))
                else:
                    messages.success(request,
                                     'تبریک! حساب شما با موفقیت فعال گردید.')
                    return redirect(reverse('home'))
            else:
                messages.success(request,
                                 'کابر گرامی حساب شما از قبل فعال بوده است.')
                return redirect('/')

        raise Http404


def logout_request(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.success(request,
                             'کاربر گرامی، برای خروج ابتدا باید وارد سایت شوید.')
            return redirect("/")
        logout(request)
        messages.success(request,
                         'کاربر گرامی، شما با موفقیت از حساب خود خارج شدید.تا دیدار بعدی بدرود.')
        return redirect("/")
    return HttpResponse('خطایی پیش آمده!')


class ForgetPasswordView(View):
    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            if form.is_valid():
                user_email = form.cleaned_data.get('email')
                user: User = User.objects.filter(email__iexact=user_email).first()
                if user is not None:
                    user.email_active_code = get_random_string(72)
                    user.save()
                    send_email_to_user('بازیابی کلمه عبور', user.email, {'user': user}, 'emails/forgot_password.html')
                    messages.success(request,
                                     'کاربر گرامی لینک بازیابی کلمه عبور به ایمل شما ارسال گردید.')
                    return JsonResponse({}, status=200)
                else:
                    form.add_error('email', 'کاربری با مشخصات وارد شده یافت نشد')
                    return JsonResponse(get_errors(form), status=401)
        return JsonResponse(get_errors(form), status=401)


class ResetPasswordView(View):
    def get(self, request: HttpRequest, activation_code):
        user: User = User.objects.filter(email_active_code__iexact=activation_code).first()
        if user is None:
            return redirect('/')

        reset_pass_form = ResetPasswordForm()

        context = {
            'reset_pass_form': reset_pass_form,
            'user': user
        }
        return render(request, 'reset_password.html', context)

    def post(self, request: HttpRequest, activation_code):
        reset_pass_form = ResetPasswordForm(request.POST)
        user: User = User.objects.filter(email_active_code__iexact=activation_code).first()
        if user is None:
            messages.error(request,
                           'کابری با لینک فعال سازی ارسال شده یافت نشد.')
            return redirect(reverse('login_page'))
        if reset_pass_form.is_valid():
            user_new_pass = reset_pass_form.cleaned_data.get('password')
            user.set_password(user_new_pass)
            user.email_active_code = get_random_string(72)
            user.is_active = True
            user.save()
            messages.success(request,
                             'تبریک! رمز عبور شما با موفقیت تغییر یافت. حالا شما می توانید با رمز عبور جدید خود وارد شوید.')
            return redirect(reverse('home'))

        context = {
            'reset_pass_form': reset_pass_form,
            'user': user
        }

        return render(request, 'reset_password.html', context)


class PersonalInfoView(View):
    def get(self, request: HttpRequest):
        if not request.user.is_authenticated:
            messages.error(request,
                           'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
            return redirect('/')
        user_model = get_object_or_404(User, id=request.user.id)
        form = EditInfoForm(request.POST or None, request.FILES or None, instance=user_model)

        context = {
            'user': user_model,
            'form': form,
        }
        return render(request, 'personal_info.html', context)

    def post(self, request: HttpRequest):
        if not request.user.is_authenticated:
            messages.error(request,
                           'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
            return redirect('/')
        user_model = get_object_or_404(User, id=request.user.id)
        form = EditInfoForm(request.POST or None, request.FILES or None, instance=user_model)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            if form.is_valid():
                instance = form.save(commit=False)
                if not instance.is_official:
                    instance.firm_economical_no = None
                    instance.firm_national_id = None
                    instance.official_address = None
                    instance.firm_tel_no = None
                    instance.firm_no = None
                    instance.organization_name = None
                instance.save()
                messages.success(request, 'کاربر گرامی مشخصات شما با موفقیت تغییر یافت.')
                return JsonResponse({}, status=200)
            else:
                return JsonResponse(get_errors(form), status=401)
        return JsonResponse(get_errors(form), status=401)


class OrdersView(View):
    def get(self, request: HttpRequest):
        if not request.user.is_authenticated:
            messages.error(request,
                           'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
            return redirect('/')
        user_model = get_object_or_404(User, id=request.user.id)
        orders = user_model.order_set.all()
        status = request.GET.get("status")
        if status and not status == '':
            orders = orders.filter(status_id=status)

        paginator = Paginator(orders, 5)
        page_number = request.GET.get("page")
        if not page_number:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        allowed_values = ['1', '2', '3']
        context = {
            'allowed_values': allowed_values,
            'user': user_model,
            'paginator': paginator,
            'page_obj': page_obj,
            'page_number': page_number,
        }
        return render(request, 'orders.html', context)


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order_details.html'
    context_object_name = 'order'


def show_invoice(request, *args, order_id=None, **kwargs):
    user = request.user
    if not user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect('/')
    user_model: User = User.objects.filter(id=user.id).first()
    if user_model.has_order_invoice:
        order: Order = Order.objects.filter(id=order_id).first()
    else:
        order = user_model.order_set.filter(id=order_id).first()
    if order.status_id not in ['1', '2', '3']:
        return Http404('فاکتور مورد نظر یافت نشد')
    t_count = order.orderitem.all_without_canceled().count()
    company_info = CompanyInfo.objects.first()
    context = {
        'company_info': company_info,
        'main_shop': CompanyInfo.objects.first(),
        'order': order,
        't_count': t_count,
    }
    html_string = render_to_string('invoice.html', context)
    response = HttpResponse(content_type='application/pdf')
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response, presentational_hints=True)
    return response


def get_errors(form):
    form_errors = []
    for field, errors in form.errors.items():
        messages = ""
        for error in errors:
            messages += error
        obj = {
            'field': field,
            'error': messages,
        }
        form_errors.append(obj)
    data = {
        'errors': form_errors
    }
    return data
