from background_task import background

from settings.models import Setting

SETTING = Setting.objects.first()
cancel_time = 3600
if SETTING:
    cancel_time = SETTING.order_cancel_time


def subtract_from_stock(items):
    for item in items:
        item.variant.quantity -= item.product_count
        item.variant.save()


def add_to_stock(items):
    for item in items:
        item.variant.quantity += item.product_count
        item.variant.save()


@background(schedule=cancel_time)
def cancel_order(order_id):
    from orders.models import Order
    order = Order.objects.filter(id=order_id).first()
    if order:
        if not order.status_id in ['2', '3']:
            order.is_canceled = True
            order.save()
            add_to_stock(order.orderitem.all())
