from django.urls import path
from . import views
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView

app_name = 'flowers'
urlpatterns = [
    path('', views.FlowerListView.as_view(), name='flower-list'),
    path('<int:flower_id>/', views.FlowerDetailView.as_view(), name='flower-detail'),
    path('create/', views.FlowerCreateView.as_view(), name='flower-create'),
    path('<int:flower_id>/update/', views.FlowerUpdateView.as_view(), name='flower-update'),
    path('<int:flower_id>/delete/', views.FlowerDeleteView.as_view(), name='flower-delete'),
    path('<int:flower_id>/add-to-cart/',views.add_to_cart,name='add-to-cart'),
]