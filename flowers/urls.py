from django.urls import path
from . import views
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView

urlpatterns = [
    path('', views.FlowerListView.as_view(), name='flower-list'),
    path('<int:pk>/', views.FlowerDetailView.as_view(), name='flower-detail'),
    path('<int:pk>/create/', views.FlowerCreateView.as_view(), name='flower-create'),
    path('<int:pk>/update/', views.FlowerUpdateView.as_view(), name='flower-update'),
    path('<int:pk>/delete/', views.FlowerDeleteView.as_view(), name='flower-delete'),
    path('<int:pk>/add-to-cart/',views.add_to_cart,name='add-to-cart'),
]