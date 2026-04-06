from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.contrib.auth.models import User
from .models import Category, FoodItem, Order, OrderItem, Cart

STATUS_CHOICES = Order.STATUS_CHOICES


def admin_required(view_func):
    """Decorator: requires user to be staff/superuser."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            from django.contrib.auth import logout
            logout(request)
            messages.error(request, 'Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_pending_count():
    return Order.objects.filter(status='pending').count()


# ─────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    total_orders    = Order.objects.count()
    pending_orders  = Order.objects.filter(status='pending').count()
    total_revenue   = Order.objects.exclude(status='cancelled').aggregate(
                        s=Sum('total_amount'))['s'] or 0
    total_customers = User.objects.filter(is_staff=False).count()
    total_items     = FoodItem.objects.count()
    total_categories = Category.objects.count()

    # Order stats by status
    status_map = dict(STATUS_CHOICES)
    order_stats = []
    for val, label in STATUS_CHOICES:
        cnt = Order.objects.filter(status=val).count()
        order_stats.append({'status': val, 'label': label, 'count': cnt})

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    # Top ordered items
    top_items = FoodItem.objects.annotate(
        order_count=Count('orderitem')
    ).select_related('category').order_by('-order_count')[:6]

    # Recent customers
    recent_customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders')
    ).order_by('-date_joined')[:6]

    return render(request, 'food_app/admin_panel/dashboard.html', {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': f'{total_revenue:,.0f}',
        'total_customers': total_customers,
        'total_items': total_items,
        'total_categories': total_categories,
        'order_stats': order_stats,
        'recent_orders': recent_orders,
        'top_items': top_items,
        'recent_customers': recent_customers,
        'pending_count': pending_orders,
    })


# ─────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_orders(request):
    search_query  = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    orders = Order.objects.select_related('user').prefetch_related(
        'order_items').order_by('-created_at')
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |
            Q(delivery_address__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'food_app/admin_panel/orders.html', {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': STATUS_CHOICES,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'food_app/admin_panel/order_detail.html', {
        'order': order,
        'status_choices': STATUS_CHOICES,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        valid = [v for v, _ in STATUS_CHOICES]
        if new_status in valid:
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {dict(STATUS_CHOICES)[new_status]}.')
        redirect_to = request.POST.get('redirect_to', 'list')
        if redirect_to == 'detail':
            return redirect('admin_order_detail', order_id=order_id)
    return redirect('admin_orders')


@admin_required
def admin_toggle_payment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.payment_status = not order.payment_status
        order.save()
        messages.success(request, f'Payment status updated for Order #{order.id}.')
    return redirect('admin_order_detail', order_id=order_id)


# ─────────────────────────────────────────────────────────────────
# FOOD ITEMS
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_food_items(request):
    search_query     = request.GET.get('search', '')
    category_filter  = request.GET.get('category', '')
    available_filter = request.GET.get('available', '')
    food_items = FoodItem.objects.select_related('category').order_by('category__name', 'name')
    if search_query:
        food_items = food_items.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query))
    if category_filter:
        food_items = food_items.filter(category_id=category_filter)
    if available_filter == '1':
        food_items = food_items.filter(is_available=True)
    elif available_filter == '0':
        food_items = food_items.filter(is_available=False)
    categories = Category.objects.all()
    return render(request, 'food_app/admin_panel/food_items.html', {
        'food_items': food_items,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'available_filter': available_filter,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_add_food_item(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            item = FoodItem.objects.create(
                name=request.POST['name'],
                description=request.POST['description'],
                price=request.POST['price'],
                category_id=request.POST['category'],
                image_url=request.POST.get('image_url', ''),
                is_vegetarian='is_vegetarian' in request.POST,
                is_featured='is_featured' in request.POST,
                is_available='is_available' in request.POST,
            )
            messages.success(request, f'"{item.name}" added successfully!')
            return redirect('admin_food_items')
        except Exception as e:
            messages.error(request, f'Error adding item: {e}')
    return render(request, 'food_app/admin_panel/food_item_form.html', {
        'categories': categories,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_edit_food_item(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            item.name         = request.POST['name']
            item.description  = request.POST['description']
            item.price        = request.POST['price']
            item.category_id  = request.POST['category']
            item.image_url    = request.POST.get('image_url', '')
            item.is_vegetarian = 'is_vegetarian' in request.POST
            item.is_featured   = 'is_featured'   in request.POST
            item.is_available  = 'is_available'  in request.POST
            item.save()
            messages.success(request, f'"{item.name}" updated successfully!')
            return redirect('admin_food_items')
        except Exception as e:
            messages.error(request, f'Error updating item: {e}')
    return render(request, 'food_app/admin_panel/food_item_form.html', {
        'item': item,
        'categories': categories,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_delete_food_item(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    name = item.name
    item.delete()
    messages.success(request, f'"{name}" deleted.')
    return redirect('admin_food_items')


@admin_required
def admin_toggle_featured(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.is_featured = not item.is_featured
    item.save()
    messages.success(request, f'"{item.name}" featured status updated.')
    return redirect('admin_food_items')


@admin_required
def admin_toggle_available(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    messages.success(request, f'"{item.name}" availability updated.')
    return redirect('admin_food_items')


# ─────────────────────────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_categories(request):
    categories = Category.objects.annotate(item_count=Count('food_items')).order_by('name')
    return render(request, 'food_app/admin_panel/categories.html', {
        'categories': categories,
        'pending_count': get_pending_count(),
    })


@admin_required
def admin_add_category(request):
    if request.method == 'POST':
        try:
            cat = Category.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
                image_url=request.POST.get('image_url', ''),
            )
            messages.success(request, f'Category "{cat.name}" added!')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return redirect('admin_categories')


@admin_required
def admin_edit_category(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == 'POST':
        cat.name        = request.POST['name']
        cat.description = request.POST.get('description', '')
        cat.image_url   = request.POST.get('image_url', '')
        cat.save()
        messages.success(request, f'Category "{cat.name}" updated!')
    return redirect('admin_categories')


@admin_required
def admin_delete_category(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    name = cat.name
    cat.delete()
    messages.success(request, f'Category "{name}" deleted.')
    return redirect('admin_categories')


# ─────────────────────────────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_customers(request):
    search_query = request.GET.get('search', '')
    customers = User.objects.filter(is_staff=False).annotate(
        order_count=Count('orders')
    ).select_related('profile').order_by('-date_joined')
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    return render(request, 'food_app/admin_panel/customers.html', {
        'customers': customers,
        'search_query': search_query,
        'pending_count': get_pending_count(),
    })


# ─────────────────────────────────────────────────────────────────
# SHOPS
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_shops(request):
    from .models import Shop
    shops = Shop.objects.select_related('manager').annotate(
        order_count=Count('orders')).order_by('name')
    return render(request, 'food_app/admin_panel/shops.html', {
        'shops': shops, 'pending_count': get_pending_count(),
    })


# ─────────────────────────────────────────────────────────────────
# DELIVERY AGENTS
# ─────────────────────────────────────────────────────────────────
@admin_required
def admin_agents(request):
    from .models import DeliveryAgent
    agents = DeliveryAgent.objects.select_related('user').annotate(
        order_count=Count('orders')).order_by('user__first_name')
    return render(request, 'food_app/admin_panel/agents.html', {
        'agents': agents, 'pending_count': get_pending_count(),
    })
