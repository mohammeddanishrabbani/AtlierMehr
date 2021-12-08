from django.shortcuts import redirect, render
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib import messages
import random
import string
from .forms import CheckoutForm
 
from .models import Product,ProductImage,Topic,Order,OrderItem,Address
# Create your views here.
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))





def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


            

def checkout(request):
    order = Order.objects.get(user=request.user, ordered=False)
    form = CheckoutForm()
    context = {
                'form': form,
                
                'order': order,
                
            }

    shipping_address_qs = Address.objects.filter(
                user=request.user,
                address_type='S',
                default=True
            )

    if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
    
    billing_address_qs = Address.objects.filter(
                user=request.user,
                address_type='B',
                default=True
            )
    

    if billing_address_qs.exists():
            context.update(
                    {'default_billing_address': billing_address_qs[0]})

    if request.method=='POST':
        form=CheckoutForm(request.POST)
        order = Order.objects.get(user=request.user, ordered=False)
        if form.is_valid():
            use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
            if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            request, "No default shipping address available")
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
                            user=request.user,
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
                        messages.info(
                            request, "Please fill in the required shipping address fields")


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
                        user=request.user,
                        address_type='B',
                        default=True
                    )

                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            request, "No default billing address available")
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
                            user=request.user,
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
                            request, "Please fill in the required billing address fields")
    
            
            
            
    return render(request, "base/checkout.html", context)

def home(request):
    return render(request,'base/home.html')


def main(request):
    return render(request,'base/main.html')



 
def shop(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    products = Product.objects.filter(Q(topic__name__icontains=q)) 
    topics=Topic.objects.all()
    context={'products':products,'topics':topics}
    return render(request, 'base/shop.html', context)


def detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    photos = ProductImage.objects.filter(product=product)
    return render(request, 'base/details.html', {
        'product':product,
        'photos':photos
    })



def add_to_cart(request, pk):
    item = get_object_or_404(Product, id=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('cart')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('detail',id=item.id)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect('detail',id=item.id)

def order_summary(request):
    order = Order.objects.get(user=request.user, ordered=False)
    context = {'object': order}
    return render(request,'base/cart.html',context)


def remove_from_cart(request, pk):
    item = get_object_or_404(Product, id=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart")


def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(Product, id=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart")