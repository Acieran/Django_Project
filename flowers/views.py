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
    context = {'use_specific_css': True}

class FlowerDetailView(DetailView):
    model = Flower
    template_name = 'flowers/flower_detail.html'

class FlowerCreateView(MyLoginRequiredMixin,CreateView):
    model = Flower
    fields = ['name', 'description', 'price', 'image', 'stock']
    template_name = 'flowers/flower_create.html'
    success_url = reverse_lazy('flowers:flower-list')

class FlowerUpdateView(MyLoginRequiredMixin,UpdateView):
    model = Flower
    fields = ['name', 'description', 'price', 'image', 'stock']
    template_name = 'flowers/flower_update.html'
    success_url = reverse_lazy('flowers:flower-list')


class FlowerDeleteView(MyLoginRequiredMixin,DeleteView):
    model = Flower
    template_name = 'flowers/flower_delete.html'
    success_url = reverse_lazy('flowers:flower-list')

def decrease_stock(request, flower_id, quantity):
    flower = get_object_or_404(Flower, id=flower_id)
    flower.stock = flower.stock - quantity
    flower.save()
