from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required ,  user_passes_test
from django.urls import reverse 
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.views.generic.base import TemplateView

from registration.models import Profile, User
from products.models import Product
from .models import Order, OrderItem , Address ,Coupon , Refunds as Refund
from .forms import CheckoutForm , PaymentForm , CouponForm , RefundForm , CouponFormUser
import stripe 
from cart.models import Payment
import random
import string

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required()
def addCart(request, id):
    item = get_object_or_404(Product, pk=id)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
        )

    order_query = Order.objects.filter(user=request.user,ordered=False)

    if order_query.exists():
        order = order_query[0]
        if order.items.filter(order=order.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,'this item quantity was update')

        else :
            order.items.add(order_item)
            messages.info(request,'this item was added to your cart')

    else :
        order_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=order_date)
        order.items.add(order_item)
        messages.info(request,'this item was added to your cart')
    
    return redirect('cartdetail')
    
@login_required()
def removeFromCart(request,id):
    item = get_object_or_404(Product, pk=id)
    order_query = Order.objects.filter(user=request.user,ordered=False)

    if order_query.exists():
        order = order_query[0]

        if order.items.filter(order=order.id).exists():
            order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                    )[0]
            order.items.remove(order_item)
            order_item.delete() 
            messages.info(request,'this item quantity was delteted from your shopping cart')
            return redirect('cartdetail')

        else :
            messages.info(request,'this item was not in your cart')
            return redirect('cartdetail')
    
    else :
        messages.info(request,'You dont have an active order')
        return redirect('cartdetail')



@login_required()
def removeSingleItemFromCart(request,id):
    item = get_object_or_404(Product, pk=id)
    order_query = Order.objects.filter(user=request.user,ordered=False)

    if order_query.exists():
        order = order_query[0]

        if order.items.filter(order=order.id).exists():
            order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                    )[0]
            if  order_item.quantity > 1 :
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete() 

            messages.info(request,'this item quantity was updated')
            return redirect('cartdetail')

        else :
            messages.info(request,'this item was not in your cart')
            return redirect('cartdetail')
    
    else :
        messages.info(request,'You dont have an active order')
        return redirect('cartdetail')


class cartdetail(View):
    def get(self, *args, **kwargs):

        try:
            order1 = Order.objects.get(user=self.request.user, ordered=False)
            order = OrderItem.objects.filter(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'object1':order1
            }
            return render(self.request, 'carts/cartdetail.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return render(self.request, 'carts/cartdetail.html')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "carts/Checkout_Form.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'C':
                    return redirect('chargeCache')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("cartdetail")

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class PaymentView(TemplateView):
    template_name = 'carts/payment.html'

    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context



def chargeCache(request):
    uerprofile = request.user.profile
    order = Order.objects.get(user=request.user, ordered=False)
    amount = int(order.get_total() * 10)
    order_items = order.items.all()
    order.ordered=True
    order.save()
    for item in order.items.all():
                item.ordered = True
                item.save()
                proID  = item.item.id
                update_quantity(request=request,id=proID)

    order.ordered = True
    order.ref_code = create_ref_code()
    order.save()
    messages.success(request, "Your order was successful!")
    return render(request, "carts/cache.html")
    

def charge(request): 
    
    if request.method == 'GET':
        order = Order.objects.get(user=request.user, ordered=False)
        if order.checkout_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = request.user.profile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(request, "payment.html", context)
        else:
            messages.warning(
                request, "You have not added a billing address")
            return redirect("checkout")


    if request.method == 'POST':
        order = Order.objects.get(user=request.user, ordered=False)
        amount = int(order.get_total() * 10)


        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                source=request.POST['stripeToken']
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order_items = order.items.all()
            order.ordered=True
            order.save()
            for item in order.items.all():
                item.ordered = True
                item.save()
                proID  = item.item.id
                update_quantity(request=request,id=proID)

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(request, "Your order was successful!")
            return  redirect("payment")

        except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(request, f"{err.get('message')}")
                return redirect("/")

        except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(request, "Rate limit error")
                return redirect("/")

        except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                messages.warning(request, "Invalid parameters")
                return redirect("/")

        except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(request, "Not authenticated")
                return redirect("/")

        except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(request, "Network error")
                return redirect("/")

        except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

        except Exception as e:
                # send an email to ourselves
                messages.warning(
                    request, "A serious error occurred. We have been notifed.")
                return redirect("/")


# generate reference code for user order
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# update product quantit after payment
def update_quantity(request,id):
    try:
        product = Product.objects.get(pk=id)
        product.quantity -= 1
        product.save()
    except Product.DoesNotExist:
        return redirect("/")
# coupon
def couponlist(request):
    coupon = Coupon.objects.all()
    return render(
        request,
        "users/admin/couponlist.html",
        {"coupon": coupon}
    )

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponFormUser(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                try:
                    coupon = Coupon.objects.get(code=code)
                except:
                    messages.success(self.request, "this coupon does not exit")
                    return redirect("checkout")

                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = getCoupon(self.request, code)
                order.save()

                messages.success(self.request, "Successfully added coupon")
                return redirect("checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("checkout")
        else:
                print(form.errors)
                messages.error(self.request, "dsfds coupon")
                return redirect("checkout")

def getCoupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("checkout")

# refund
def RequestRefund(request):
    if request.method == "GET":
        form = RefundForm()
        context = {
            'form': form
        }
        return render(request, "carts/request_refund.html", context)

    else:
        form = RefundForm(request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(request, "Your request was received.")
                return redirect("request-refund")

            except ObjectDoesNotExist:
                messages.info(request, "This order does not exist.")
                return redirect("request-refund")


from django.views.generic import View
from django.utils import timezone
from .models import *
from .render import Render


class Pdf(View):

    def get(self, request):
        user = request.user
        orders = OrderItem.objects.filter(user=request.user)
        today = timezone.now()
        params = {
            'today': today,
            'orders': orders,
            'user': user
        }
        return Render.render('pdf.html', params)

