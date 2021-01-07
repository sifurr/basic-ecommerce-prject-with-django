from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
# Models and Forms
from app_order.models import Order
from app_payment.models import BillingAddress
from app_payment.forms import BillingForm

# Login authentication
from django.contrib.auth.decorators import login_required

# For Payment with SSLCommerz
import requests
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
from django.views.decorators.csrf import csrf_exempt

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
    return render(request, 'app_payment/checkout.html', context={'form': form, 'order_items': order_items, 'order_total': order_total, 'saved_address': saved_address})


@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    if not saved_address.is_fully_filled():
        messages.info(request, f'Please complete shipping address!')
        return redirect('app_payment:checkout')

    if not request.user.profile.is_fully_filled():
        messages.info(request, f'Please compleate your pprofile details!')
        return redirect('app_login:profile')

    # SSLCommerz
    store_id = 'hight5ff699be52b6b'
    API_key = 'hight5ff699be52b6b@ssl'
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id,
                            sslc_store_pass=API_key)

    status_url = request.build_absolute_uri(reverse('app_payment:complete'))
    # print(status_url)
    mypayment.set_urls(success_url=status_url, fail_url=status_url,
                       cancel_url=status_url, ipn_url=status_url)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderItems.all()
    order_items_count = order_qs[0].orderItems.count()
    order_total = order_qs[0].get_totals()
    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed',
                                      product_name=order_items, num_of_item=order_items_count, shipping_method='Courier', product_profile='None')

    current_user = request.user
    mypayment.set_customer_info(name=current_user.profile.full_name, email=current_user.email, address1=current_user.profile.address_1,
                                address2=current_user.profile.address_1, city=current_user.profile.city, postcode=current_user.profile.zipcode, country=current_user.profile.country, phone=current_user.profile.phone)

    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name, address=saved_address.address,
                                city=saved_address.city, postcode=saved_address.zipcode, country=saved_address.country)
    response_data = mypayment.init_payment()
    print(response_data)
    return redirect(response_data['GatewayPageURL'])


@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']

        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            bank_tran_id = payment_data['bank_tran_id']
            messages.success(
                request, f"Your Payment Completed Successfully! Page will be redirected.")
        elif status == 'FAILED':
            messages.warning(
                request, f"Your Payment Failed! Please Try Again! Page will be redirected.")
    print(payment_data)
    return render(request, 'app_payment/complete.html', context={})
