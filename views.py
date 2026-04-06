from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import (FoodItem, Category, Cart, CartItem, Order, OrderItem,
                     UserProfile, Shop, DeliveryAgent, OrderTrackingLog)
from .forms import RegisterForm, LoginForm, OrderForm, ProfileForm


def home(request):
    shops         = Shop.objects.filter(is_open=True).prefetch_related('food_items')
    featured      = FoodItem.objects.filter(is_featured=True, is_available=True).select_related('shop')[:8]
    categories    = Category.objects.all()
    all_items     = FoodItem.objects.filter(is_available=True).select_related('category', 'shop')
    menu_data     = []
    for cat in categories:
        items = [i for i in all_items if i.category_id == cat.id]
        if items:
            menu_data.append({'category': cat, 'items': items})
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_item_count()
    return render(request, 'food_app/home.html', {
        'shops': shops, 'featured_items': featured,
        'categories': categories, 'menu_data': menu_data,
        'cart_count': cart_count,
    })


def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    items = FoodItem.objects.filter(shop=shop, is_available=True).select_related('category')
    categories = Category.objects.filter(food_items__shop=shop).distinct()
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_item_count()
    return render(request, 'food_app/shop_detail.html', {
        'shop': shop, 'items': items, 'categories': categories,
        'cart_count': cart_count,
    })


def menu(request):
    categories    = Category.objects.all()
    shops         = Shop.objects.filter(is_open=True)
    category_id   = request.GET.get('category')
    shop_id       = request.GET.get('shop')
    search_query  = request.GET.get('search', '')
    food_items    = FoodItem.objects.filter(is_available=True).select_related(
                        'category', 'shop').order_by('category__name', 'name')
    if category_id:
        food_items = food_items.filter(category_id=category_id)
    if shop_id:
        food_items = food_items.filter(shop_id=shop_id)
    if search_query:
        food_items = food_items.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query) |
            Q(item_code__icontains=search_query))
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_item_count()
    return render(request, 'food_app/menu.html', {
        'categories': categories, 'shops': shops, 'food_items': food_items,
        'selected_category': category_id, 'selected_shop': shop_id,
        'search_query': search_query, 'cart_count': cart_count,
    })


def food_detail(request, food_id):
    item = get_object_or_404(FoodItem, id=food_id)
    related = FoodItem.objects.filter(
        category=item.category, is_available=True).exclude(id=food_id)[:4]
    return render(request, 'food_app/food_detail.html',
                  {'food_item': item, 'related_items': related})


@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.cart_items.select_related('food_item__shop').all()
    return render(request, 'food_app/cart.html',
                  {'cart': cart_obj, 'cart_items': items, 'total': cart_obj.get_total()})


@login_required
def add_to_cart(request, food_id):
    food_item = get_object_or_404(FoodItem, id=food_id, is_available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    ci, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
    if not created:
        ci.quantity += 1; ci.save()
    messages.success(request, f'"{food_item.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'menu'))


@login_required
def remove_from_cart(request, item_id):
    ci = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    ci.delete()
    messages.success(request, 'Item removed.')
    return redirect('cart')


@login_required
def update_cart(request, item_id):
    ci = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    qty = int(request.POST.get('quantity', 1))
    if qty <= 0:
        ci.delete()
    else:
        ci.quantity = qty; ci.save()
    return redirect('cart')


@login_required
def checkout(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    items = cart_obj.cart_items.select_related('food_item__shop').all()
    if not items.exists():
        messages.warning(request, 'Cart is empty.')
        return redirect('menu')
    total = cart_obj.get_total()
    # Determine shop from cart items
    shop = None
    if items.first() and items.first().food_item.shop:
        shop = items.first().food_item.shop

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user, shop=shop,
                delivery_address=form.cleaned_data['delivery_address'],
                phone_number=form.cleaned_data['phone_number'],
                payment_method=form.cleaned_data['payment_method'],
                special_instructions=form.cleaned_data.get('special_instructions', ''),
                total_amount=total,
            )
            for ci in items:
                OrderItem.objects.create(
                    order=order, food_item=ci.food_item,
                    quantity=ci.quantity, price=ci.food_item.price)
            OrderTrackingLog.objects.create(
                order=order, status='pending',
                message=f'Order #{order.id} placed successfully. Waiting for shop to accept.',
                actor=request.user)
            items.delete()
            messages.success(request, f'Order #{order.id} placed!')
            return redirect('order_detail', order_id=order.id)
    else:
        profile = getattr(request.user, 'profile', None)
        form = OrderForm(initial={
            'delivery_address': profile.address if profile else '',
            'phone_number': profile.phone if profile else '',
        })
    return render(request, 'food_app/checkout.html', {
        'form': form, 'cart_items': items, 'total': total, 'shop': shop})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    logs  = order.tracking_logs.all()
    return render(request, 'food_app/order_detail.html',
                  {'order': order, 'logs': logs})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'food_app/my_orders.html', {'orders': orders})


@login_required
def profile(request):
    up, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=up)
        if form.is_valid():
            form.save()
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name  = request.POST.get('last_name', '')
            request.user.email      = request.POST.get('email', '')
            request.user.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=up, initial={
            'first_name': request.user.first_name,
            'last_name':  request.user.last_name,
            'email':      request.user.email,
        })
    return render(request, 'food_app/profile.html', {
        'form': form,
        'orders_count': Order.objects.filter(user=request.user).count(),
    })


# ── AUTH ───────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role='customer')
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('menu')
    return render(request, 'food_app/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    error_message = None
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                # Role-based redirect
                profile = getattr(user, 'profile', None)
                if profile:
                    if profile.role == 'shop_manager':
                        return redirect('shop_manager_dashboard')
                    if profile.role == 'delivery_agent':
                        return redirect('agent_dashboard')
                return redirect(request.GET.get('next', 'home'))
            else:
                error_message = 'Invalid username or password.'
    return render(request, 'food_app/login.html',
                  {'form': form, 'error_message': error_message})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out.')
    return redirect('home')


# ── SHOP MANAGER DASHBOARD ─────────────────────────────────────────
@login_required
def shop_manager_dashboard(request):
    try:
        shop = request.user.shop
    except Shop.DoesNotExist:
        messages.error(request, 'No shop linked to your account.')
        return redirect('home')
    orders = Order.objects.filter(shop=shop).order_by('-created_at')
    pending  = orders.filter(status='pending')
    active   = orders.filter(status__in=['shop_accepted','preparing','ready_for_pickup'])
    agents   = DeliveryAgent.objects.filter(status='available').select_related('user')
    return render(request, 'food_app/shop_manager/dashboard.html', {
        'shop': shop, 'orders': orders, 'pending': pending,
        'active': active, 'agents': agents,
    })


@login_required
def shop_accept_order(request, order_id):
    shop = get_object_or_404(Shop, manager=request.user)
    order = get_object_or_404(Order, id=order_id, shop=shop)
    order.status = 'shop_accepted'
    order.shop_accepted_at = timezone.now()
    order.save()
    OrderTrackingLog.objects.create(
        order=order, status='shop_accepted',
        message=f'{shop.name} has accepted your order and will start preparing soon.',
        actor=request.user)
    messages.success(request, f'Order #{order.id} accepted.')
    return redirect('shop_manager_dashboard')


@login_required
def shop_update_order(request, order_id):
    shop  = get_object_or_404(Shop, manager=request.user)
    order = get_object_or_404(Order, id=order_id, shop=shop)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        agent_id   = request.POST.get('agent_id')
        messages_map = {
            'preparing':        'Your food is being prepared by our chefs.',
            'ready_for_pickup': 'Your order is ready! Waiting for a delivery agent.',
            'cancelled':        'Your order has been cancelled by the shop.',
        }
        if new_status in messages_map:
            order.status = new_status
            if new_status == 'ready_for_pickup' and agent_id:
                try:
                    agent = DeliveryAgent.objects.get(id=agent_id, status='available')
                    order.delivery_agent = agent
                    order.status = 'agent_assigned'
                    order.agent_assigned_at = timezone.now()
                    agent.status = 'on_delivery'; agent.save()
                    OrderTrackingLog.objects.create(
                        order=order, status='agent_assigned',
                        message=f'Delivery agent {agent.user.get_full_name()} ({agent.vehicle}) has been assigned.',
                        actor=request.user)
                except DeliveryAgent.DoesNotExist:
                    pass
            else:
                OrderTrackingLog.objects.create(
                    order=order, status=new_status,
                    message=messages_map.get(new_status, f'Status updated to {new_status}.'),
                    actor=request.user)
            order.save()
            messages.success(request, f'Order #{order.id} updated to {new_status}.')
    return redirect('shop_manager_dashboard')


# ── DELIVERY AGENT DASHBOARD ───────────────────────────────────────
@login_required
def agent_dashboard(request):
    try:
        agent = request.user.delivery_agent
    except DeliveryAgent.DoesNotExist:
        messages.error(request, 'No delivery agent profile found.')
        return redirect('home')
    my_orders = Order.objects.filter(
        delivery_agent=agent).order_by('-created_at')
    active = my_orders.filter(status__in=['agent_assigned','out_for_delivery'])
    return render(request, 'food_app/agent/dashboard.html', {
        'agent': agent, 'my_orders': my_orders, 'active': active,
    })


@login_required
def agent_update_order(request, order_id):
    agent = get_object_or_404(DeliveryAgent, user=request.user)
    order = get_object_or_404(Order, id=order_id, delivery_agent=agent)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'pickup':
            order.status = 'out_for_delivery'
            order.save()
            OrderTrackingLog.objects.create(
                order=order, status='out_for_delivery',
                message=f'Your order has been picked up by {agent.user.get_full_name()} and is on the way!',
                actor=request.user)
            messages.success(request, 'Marked as Out for Delivery.')
        elif action == 'deliver':
            order.status = 'delivered'
            order.delivered_at = timezone.now()
            order.save()
            agent.status = 'available'; agent.save()
            OrderTrackingLog.objects.create(
                order=order, status='delivered',
                message='Order delivered successfully! Enjoy your meal 🎉',
                actor=request.user)
            messages.success(request, f'Order #{order.id} marked as Delivered.')
    return redirect('agent_dashboard')
