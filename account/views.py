from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from .forms import UserForm, UserUpdateForm, AuthenticationForm  # Create these forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from orders.models import Order #Import Order model
from django.urls import reverse

def register_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after successful registration
            return redirect('account:profile')
    else:
        form = UserForm()
    return render(request, 'account/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('account:profile') # Redirect to profile after login
            else:
                return render(request, 'account/login.html', {'form': form, 'error_message': 'Invalid credentials'})
    else:
        form = AuthenticationForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    return redirect('account:login')

@login_required
def get_profile(request):
    return render(request, 'account/profile.html', {'user': request.user})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'account/profile_update.html', {'form': form})


@login_required
def get_order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/order_history.html', {'orders': orders})

# Admin-like views (These should be protected with appropriate permissions/authentication):

def get_users(request):
    if not request.user.is_superuser: #Check if superuser
        return redirect('account:profile') #Redirect to profile if not superuser
    users = User.objects.all()
    return render(request, 'account/account_list.html', {'users': users})

def update_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('account:profile')
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('account:get_users')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'account/account_update.html', {'form': form, 'user': user})


@login_required(login_url='account:login')
def delete_user(request, user_id):
    if not request.user.is_superuser:  # Crucial security check!
        return redirect('account:profile')

    user = get_object_or_404(User, pk=user_id)
    next_url = request.GET.get('next') or reverse('account:get_users') # Handle GET for redirection

    if request.method == 'POST':
        user.delete()
        return redirect(next_url)  # Redirect to the intended URL.

    return render(request, 'account/account_delete.html', {'user': user})