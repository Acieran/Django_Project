import json

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from flowers.views import decrease_stock
from .models import Order, OrderItem
from flowers.models import Flower # Import the Flower model
from django.contrib.auth.decorators import login_required
from django.contrib import messages #For messages
# TODO update shipping information of order from user
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

def get_order_items(request, order_id):
    """
    Retrieves OrderItems associated with a specific order ID.

    Args:
        request: Request object.
        order_id: The ID of the order.

    Returns:
        A QuerySet of OrderItem objects, or None if no order exists.  Raises an exception if the user doesn't own the order.
        Returns an empty QuerySet if no order items are found.
    """

    try:
        order = get_object_or_404(Order, pk=order_id)
        #Important check to make sure the user can view the order items
        if order.user.id != request.user.id and not(request.user.is_staff or request.user.is_superuser):  # Example: Assuming you have a request.user
            raise PermissionDenied("You do not have permission to view this order.")
        order_items = order.orderitem_set.all()
        return order_items
    except Order.DoesNotExist:
        return None # or raise an exception, depending on desired behavior
    except PermissionDenied as e:
        raise e #Re-raise the exception

def get_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = get_order_items(request, order_id)
    return render(request, 'orders/order_detail.html', {'order': order, 'order_items': order_items})

@login_required
def create_order(request):
    if request.method == 'POST':
        try:
            with (transaction.atomic()):  # Crucial for data integrity
                cart_items = request.session.get('cart', {})
                if not cart_items:
                    messages.error(request, 'Your cart is empty.')
                    return redirect('orders:cart')

                total_price = 0
                order = Order.objects.create(user=request.user, total_amount=total_price)
                for flower_id, quantity in cart_items.items():
                    try:
                        flower = Flower.objects.get(pk=flower_id)
                        if flower.stock < quantity:
                            messages.error(request, f"Insufficient stock for {flower.name}.")
                            return redirect('orders:cart')  # Or handle differently.
                        total_price += flower.price * quantity
                        order_item = OrderItem.objects.create(order_id=order.id, quantity=quantity, flower=flower)
                        order_item.save()
                        decrease_stock(request, flower_id, quantity)
                    except Flower.DoesNotExist:
                        messages.error(request, f"Flower with ID {flower_id} not found.")
                        return redirect('orders:cart')
                    except ValueError as e:
                        messages.error(request, f"Invalid quantity: {e}")
                        return redirect('orders:cart')

                try:
                    order.total_amount = total_price
                    order.save()
                except Exception as e:
                    import traceback
                    print(f"Exception during item.save(): {e}")
                    traceback.print_exc()  # Print the full traceback
                    messages.error(request, f"A database error occurred during order placement: {e}")
                    return redirect('orders:cart')  # redirect back to cart

                del request.session['cart']  # Important: Clear the session cart
                messages.success(request, 'Your order has been placed!')
                return redirect('orders:order_detail', order_id=order.id)
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('orders:cart')
    else:
        return redirect('orders:cart')



@login_required
def order_update(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)
        order_items = get_order_items(request, order_id)
        if request.method == 'POST':
            for item in order_items: # Correct access to many-to-many
                new_quantity = request.POST.get(f'quantity_{item.id}')
                try:
                    new_quantity = int(new_quantity)
                    if new_quantity < 0:
                        messages.error(request, "Invalid Quantity")
                        return HttpResponseRedirect(request.path)
                    decrease_stock(request, item.flower_id, new_quantity - item.quantity)
                    item.quantity = new_quantity
                    item.save()
                except ValueError:
                    messages.error(request, "Invalid quantity")
                    return HttpResponseRedirect(request.path)
            messages.success(request, "Order updated successfully!")
            return redirect('orders:order_detail', order_id=order_id)
        return render(request, 'orders/order_update.html', {'order': order, 'order_items': order_items})
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('flowers:flower_list')
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect('flowers:flower_list')

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    if request.method == 'POST':
        order_items = get_order_items(request, order_id)
        for item in order_items:
            decrease_stock(request, item.flower_id, -item.quantity)
            item.delete()
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

            current_cart = request.session.get('cart', {}) #Get cart from session
            current_cart[flower_id] = current_cart.get(flower_id, 0) + quantity #Add or update quantity
            request.session['cart'] = current_cart #Save cart back to session
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
    current_cart = request.session.get('cart', {})
    if flower_id in current_cart:
      del current_cart[flower_id]
      request.session['cart'] = current_cart
    return redirect('orders:cart')

@login_required
def cart(request):
    current_cart = request.session.get('cart', {})
    flowers_queryset = Flower.objects.all()  # Your existing queryset
    flowers = {flower.id: flower for flower in flowers_queryset}
    total_price = 0
    subtotals = {} # Dictionary to store subtotals

    for flower_id, quantity in current_cart.items():
        try:
            flower = flowers_queryset.get(pk=flower_id)
            subtotal = flower.price * quantity  # Calculate subtotal here
            total_price += subtotal
            subtotals[flower.id] = subtotal #Store the subtotal
        except Flower.DoesNotExist:
            # Handle the case where a flower is no longer available
            pass

    context = {'cart': current_cart, 'flowers': flowers, 'total_price': total_price, 'subtotals': subtotals}
    return render(request, 'orders/cart.html', context)