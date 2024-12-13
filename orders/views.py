import datetime
import math

from django.contrib import messages
from django.http import HttpRequest, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST

from orders.Tasks import subtract_from_stock, cancel_order
from settings.models import Financials
from u_account.models import User
from u_account.views import get_errors
from orders.forms import CartForm
from orders.models import Order, OrderItem, Invoice
from product.models import ProductInventory


# Create your views here.


class AddToCartView(View):
    def post(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return JsonResponse({}, status=401)
        variant_id = request.POST.get('variant')
        variant = get_object_or_404(ProductInventory, id=variant_id)
        form = CartForm(request.POST)
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            if form.is_valid():
                if not request.user.info_is_complete():
                    form.add_error('variant_count', 'جهت ادامه ثبت سفارش ابتدا اطلاعات فردی یا حقوقی را در پروفایل خود کامل نمایید!')
                    return JsonResponse(get_errors(form), status=400)
                order = Order.objects.filter(customer=request.user, status_id=0).first()
                if order is None:
                    order = Order.objects.create(customer=request.user, status_id=0)
                cd = form.cleaned_data
                item = order.orderitem.filter(variant=variant).first()
                if item:
                    if variant.in_basket >= cd['variant_count'] + item.product_count and variant.unit > 0 and variant.quantity >= cd['variant_count'] + item.product_count:
                        item.product_count += cd['variant_count']
                        item.unit_qty = variant.unit
                    item.save()
                else:
                    if variant.in_basket >= cd['variant_count'] and variant.quantity >= cd['variant_count'] and variant.unit > 0:
                        item = order.orderitem.create(variant=variant,unit_qty=variant.unit, product_price=variant.price,supplement_price=variant.supplement_price,product_count=cd['variant_count'],item=variant.__str__())
                return JsonResponse({}, status=200)
            else:
                return JsonResponse(get_errors(form), status=400)
        return JsonResponse(get_errors(form), status=400)

@require_POST
def update_cart(request, item_id):
    user = request.user
    if not user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect(reverse('home'))
    cart_form = CartForm(request.POST)
    if cart_form.is_valid():
        cd = cart_form.cleaned_data
        item = get_object_or_404(OrderItem, id=item_id)
        item.product_count = cd['variant_count']
        item.unit_qty = item.variant.unit
        item.save()
    return redirect('orders:cart')


@require_POST
def cart_remove(request, variant_id):
    user = request.user
    if not user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect(reverse('home'))
    item = OrderItem.objects.filter(order__customer=user, id=variant_id,order__status_id=0).first()
    order = item.order
    if item:
        item.delete()
        if order.orderitem.count() == 0:
            order.delete()
    else:
        raise Http404()
    return redirect('orders:cart')


def cart(request):
    if not request.user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect('/')
    order = Order.objects.filter(customer=request.user, status_id=0).first()
    if not order:
        messages.error(request,
                       'سبد خرید شما خالی است!')
        return redirect(reverse('products:search'))
    else:
        cart_msgs = apply_order_changes(order)
    context = {
        'order':order,
        'cart_msgs':cart_msgs,
    }
    return render(request, 'cart.html', context)

@require_POST
def remove_items(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect('/')
    order = Order.objects.filter(customer=request.user, status_id=0).first()
    if order:
        order.delete()
    return redirect('/')

def complete_shopping(request):
    user = request.user
    if not user.is_authenticated:
        messages.error(request,
                       'شما می بایست ابتدا وارد حساب کاربری خود شوید!')
        return redirect(reverse('home'))

    user = User.objects.filter(id=user.id).first()
    order : Order = Order.objects.filter(customer=request.user, status_id=0).first()
    if order:
        order.status_id = 1
        order.order_date = datetime.datetime.now()
        for item in order.orderitem.all():
            item.unit_qty = item.variant.unit
            item.save()

        invoice : Invoice = Invoice.objects.filter(order=order).first()
        if not invoice:
            invoice = Invoice.objects.create(order=order)
        invoice.invoice_date = order.order_date
        if user.is_official:
            invoice.is_official = True
            invoice.organization_name = user.organization_name
            invoice.firm_no = user.firm_no
            invoice.firm_national_id = user.firm_national_id
            invoice.firm_economical_no = user.firm_economical_no
            invoice.full_address = user.official_address
            invoice.tel_no = user.tel_no
            invoice.postal_code = user.official_postal_code
        else:
            invoice.is_official = False
            invoice.full_name = user.get_full_name()
            invoice.first_name = user.first_name
            invoice.last_name = user.last_name
            invoice.mobile = user.mobile
            invoice.national_code = user.national_code
            invoice.full_address = user.personal_address
            invoice.postal_code = user.postal_code
        invoice.save()
        order.save()
        subtract_from_stock(order.orderitem.all())
        cancel_order(order.id)
        messages.error(request,
                       'سفارش شما با موفقیت ثبت گردید!')
        return redirect(reverse('account:orders'))
    else:
        messages.error(request,
                       'سفارش مورد نظر یافت نشد!')
        return redirect(reverse('home'))


def apply_order_changes(order):
    message = []
    for item in order.orderitem.all():
        if item.variant.quantity < item.product_count:
            if item.variant.quantity == 0:
                item.delete()
                obj = f"ایتم {item.variant} به دلیل نداشتن موجودی از سبد خرید حذف گردید."
                message.append(obj)
            else:
                item.product_count = item.variant.quantity
                item.save()
                obj = f" تعداد آیتم  {item.variant} به دلیل کم بودن موجودی در انبار به {item.product_count} عدد تغییر یافت."
                message.append(obj)
        if item.variant.in_basket < item.product_count:
            item.product_count = item.variant.in_basket
            item.save()
            obj = f" تعداد آیتم  {item.variant} به دلیل بیشتر بودن از تعداد مجاز در سبد، به {item.product_count} عدد تغییر یافت."
            message.append(obj)
        if item.variant.price != item.product_price:
            item.product_price = item.variant.price * item.variant.unit
            item.save()
            new_price = '{:,}'.format(math.trunc(item.variant.price))
            obj = f"قیمت {item.variant} شما در سبد به {new_price} تومان تغییر یافته است!"
            message.append(obj)
    return message
