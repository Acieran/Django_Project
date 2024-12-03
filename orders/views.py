from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Order
from flowers.models import Flower # Import the Flower model
from django.contrib.auth.decorators import login_required
from django.contrib import messages #For messages


@login_required
def get_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


def get_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})



@login_required
def create_order(request):
    if request.method == 'POST':
        # Get cart items (Replace with your cart logic)
        cart_items = request.session.get('cart', [])
        if not cart_items:
            messages.error(request, 'Your cart is empty.')
            return redirect('flowers:flower_list')

        total_price = 0
        order_items = []
        for item_id, quantity in cart_items.items():
            flower = get_object_or_404(Flower, pk=item_id)
            total_price += flower.price * quantity
            order_items.append(OrderItem(flower=flower, quantity=quantity))

        order = Order.objects.create(user=request.user, total_price=total_price)
        OrderItem.objects.bulk_create(order_items)
        del request.session['cart']
        messages.success(request, 'Your order has been placed!')
        return redirect('orders:order_detail', order_id=order.id)

    else:
        return redirect('flowers:flower_list')


@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        # Handle order update logic here
        pass
    return render(request, 'orders/order_update.html', {'order': order})

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted.')
        return redirect('orders:order_list')
    return render(request, 'orders/order_delete.html', {'order': order})

@login_required
def add_to_cart(request, flower_id):
    flower = get_object_or_404(Flower, pk=flower_id)
    cart = request.session.get('cart', {})
    cart[flower_id] = cart.get(flower_id, 0) + 1
    request.session['cart'] = cart
    return redirect('orders:cart')

@login_required
def remove_from_cart(request, flower_id):
    flower = get_object_or_404(Flower, pk=flower_id)
    cart = request.session.get('cart', {})
    if flower_id in cart:
      del cart[flower_id]
      request.session['cart'] = cart
    return redirect('orders:cart')

@login_required
def cart(request):
    cart = request.session.get('cart', {})
    return render(request, 'orders/cart.html', {'cart': cart})

@login_required
def checkout(request):
    #Add your checkout logic here
    return render(request, 'orders/checkout.html')