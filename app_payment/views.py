from django.shortcuts import render
from django.contrib import messages
# Models and Forms
from app_order.models import Order
from app_payment.models import BillingAddress
from app_payment.forms import BillingForm

# Login authentication
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == 'POST':
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request, f'Shipping Address Saved')
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # print(order_qs)
    order_items = order_qs[0].orderItems.all()
    # print(order_items)
    order_total = order_qs[0].get_totals()
    return render(request, 'app_payment/checkout.html', context={'form': form, 'order_items': order_items, 'order_total': order_total})
