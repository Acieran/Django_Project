import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import Order, FlowerCart
from flowers.models import Flower # Import the Flower model
from django.contrib.auth.decorators import login_required
from django.contrib import messages #For messages
# TODO Make all htmls and check logic

@login_required
def get_orders(request):
    orders = Order.objects.filter(user=request.user)
    paginator = Paginator(orders, 10) # Show 10 orders per page

    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)

    return render(request, 'orders/order_list.html', {'orders': orders, 'paginator': paginator})


def get_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    flower_сart = order.flowerCart
    return render(request, 'orders/order_detail.html', {'order': order, 'flowerCart': flower_сart})


@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():  # Crucial for data integrity
                cart_items = request.session.get('cart', {})
                if not cart_items:
                    messages.error(request, 'Your cart is empty.')
                    return redirect('flowers:flower_list')

                total_price = 0
                order_items = []
                for flower_id, quantity in cart_items.items():
                    try:
                        flower = Flower.objects.get(pk=flower_id)
                        if flower.stock < quantity:
                            messages.error(request, f"Insufficient stock for {flower.name}.")
                            return redirect('flowers:flower_list')  # Or handle differently.
                        total_price += flower.price * quantity
                        order_items.append(FlowerCart(flower=flower, quantity=quantity))

                    except Flower.DoesNotExist:
                        messages.error(request, f"Flower with ID {flower_id} not found.")
                        return redirect('flowers:flower_list')
                    except ValueError as e:
                        messages.error(request, f"Invalid quantity: {e}")
                        return redirect('flowers:flower_list')

                order = Order.objects.create(user=request.user, total_amount=total_price, )  # Corrected field name

                # Use bulk_create for efficiency
                try:
                    for item in order_items:
                        item.user = request.user
                        item.save()
                except Exception as e:
                    import traceback
                    print(f"Exception during item.save(): {e}")
                    traceback.print_exc()  # Print the full traceback
                    messages.error(request, f"A database error occurred during order placement: {e}")
                    return redirect('flowers:flower_list')  # redirect back to cart

                del request.session['cart']  # Important: Clear the session cart
                messages.success(request, 'Your order has been placed!')
                return redirect('orders:order_detail', order_id=order.id)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('flowers:flower-list')
    else:
        return redirect('flowers:flower-list')


@login_required
def order_update(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)

        if request.method == 'POST':
            for item in order.flowerCart.all(): # Correct access to many-to-many
                new_quantity = request.POST.get(f'quantity_{item.id}')
                try:
                    new_quantity = int(new_quantity)
                    if new_quantity < 0:
                        messages.error(request, "Invalid Quantity")
                        return HttpResponseRedirect(request.path)
                    item.quantity = new_quantity
                    item.save()
                except ValueError as e:
                    messages.error(request, "Invalid quantity")
                    return HttpResponseRedirect(request.path)
            messages.success(request, "Order updated successfully!")
            return redirect('orders:order_detail', order_id=order_id)
        return render(request, 'orders/order_update.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('flowers:flower_list')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('flowers:flower_list')

@login_required
@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted.')
        return redirect('orders:order_list')
    return render(request, 'orders/order_delete.html', {'order': order})


@csrf_exempt
@login_required
def add_to_cart(request, flower_id):
    if request.method == 'POST':
        try:
            data_str = request.body.decode('utf-8')  # Decode from bytes to string
            data_dict = json.loads(data_str)  # Parse JSON string into a dictionary

            quantity = data_dict['quantity']  # Access the 'quantity' value
            flower = Flower.objects.get(pk=flower_id) #Get flower from DB

            if flower.stock < quantity:
                return JsonResponse({'success': False, 'message': 'Insufficient stock.'})

            cart = request.session.get('cart', {}) #Get cart from session
            cart[flower_id] = cart.get(flower_id, 0) + quantity #Add or update quantity
            request.session['cart'] = cart #Save cart back to session
            request.session.modified = True #Important to signal session change
            return JsonResponse({'success': True, 'message': 'Item added to cart'})

        except Flower.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Flower not found.'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid quantity.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


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
    flowers_queryset = Flower.objects.all()  # Your existing queryset
    flowers = {flower.id: flower for flower in flowers_queryset}
    total_price = 0
    subtotals = {} # Dictionary to store subtotals

    for flower_id, quantity in cart.items():
        try:
            flower = flowers_queryset.get(pk=flower_id)
            subtotal = flower.price * quantity  # Calculate subtotal here
            total_price += subtotal
            subtotals[flower.id] = subtotal #Store the subtotal
        except Flower.DoesNotExist:
            # Handle the case where a flower is no longer available
            pass

    context = {'cart': cart, 'flowers': flowers, 'total_price': total_price, 'subtotals': subtotals}
    return render(request, 'orders/cart.html', context)

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    flowers = Flower.objects.all()
    total_price = 0
    for flower_id, quantity in cart.items():
        try:
            flower = flowers.get(pk=flower_id)
            total_price += flower.price * quantity
        except Flower.DoesNotExist:
            # Handle unavailable flowers
            pass
    return render(request, 'orders/checkout.html', {'cart': cart, 'flowers': flowers, 'total_price': total_price})
