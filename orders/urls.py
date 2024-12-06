from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'orders'
urlpatterns = [
    path('', login_required(views.get_orders), name='order_list'), #List of Orders
    path('<int:order_id>/', login_required(views.get_order), name='order_detail'), #Order detail
    path('create/', login_required(views.create_order), name='create_order'), #Create Order
    path('<int:order_id>/update/', login_required(views.order_update), name='order_update'), #Update Order
    path('<int:order_id>/delete/', login_required(views.delete_order), name='order_delete'), #Delete Order
    path('cart/', login_required(views.cart), name='cart'), #Cart View
    path('add-to-cart/<int:flower_id>/', login_required(views.add_to_cart), name='add_to_cart'), #Add to cart
    path('remove-from-cart/<int:flower_id>/', login_required(views.remove_from_cart), name='remove_from_cart'), #Remove from cart
    path('checkout/', login_required(views.checkout), name='checkout'), #Checkout View


]