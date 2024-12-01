from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .models import Flower
from orders.models import FlowerCart
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin



class MyLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy('account:login')  # Example: Login view

class FlowerListView(ListView):
    model = Flower
    template_name = 'flowers/flower_list.html'
    context_object_name = 'flowers'

class FlowerDetailView(DetailView):
    model = Flower
    template_name = 'flowers/flower_detail.html'

class FlowerCreateView(MyLoginRequiredMixin,CreateView):
    model = Flower
    fields = ['name', 'description', 'price', 'image']
    template_name = 'flowers/flower_create.html'

class FlowerUpdateView(MyLoginRequiredMixin,UpdateView):
    model = Flower
    fields = ['name', 'description', 'price', 'image']
    template_name = 'flowers/flower_update.html'


class FlowerDeleteView(MyLoginRequiredMixin,DeleteView):
    model = Flower
    template_name = 'flowers/flower_delete.html'
    success_url = '/flowers/'

def add_to_cart(request,flower_id):
    if request.method == 'POST':
        flower = get_object_or_404(Flower,flower_id=flower_id)
        quantity = request.POST.get('quantity')
        cart_item, created = FlowerCart.objects.get_or_create(user=request.user,flower=flower)
        if created:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.quantity +=int(quantity)
            cart_item.save()
        return redirect('flower-list')
    else:
        return redirect('flower-list')
