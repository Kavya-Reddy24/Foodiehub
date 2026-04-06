from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('shops/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('menu/', views.menu, name='menu'),
    path('menu/<int:food_id>/', views.food_detail, name='food_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Shop Manager ───────────────────────────────────────────────
    path('shop-manager/', views.shop_manager_dashboard, name='shop_manager_dashboard'),
    path('shop-manager/orders/<int:order_id>/accept/', views.shop_accept_order, name='shop_accept_order'),
    path('shop-manager/orders/<int:order_id>/update/', views.shop_update_order, name='shop_update_order'),

    # ── Delivery Agent ─────────────────────────────────────────────
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/orders/<int:order_id>/update/', views.agent_update_order, name='agent_update_order'),

    # ── Custom Admin Panel ──────────────────────────────────────────
    path('foodadmin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('foodadmin/orders/', admin_views.admin_orders, name='admin_orders'),
    path('foodadmin/orders/<int:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('foodadmin/orders/<int:order_id>/status/', admin_views.admin_update_order_status, name='admin_update_order_status'),
    path('foodadmin/orders/<int:order_id>/payment/', admin_views.admin_toggle_payment, name='admin_toggle_payment'),
    path('foodadmin/food-items/', admin_views.admin_food_items, name='admin_food_items'),
    path('foodadmin/food-items/add/', admin_views.admin_add_food_item, name='admin_add_food_item'),
    path('foodadmin/food-items/<int:item_id>/edit/', admin_views.admin_edit_food_item, name='admin_edit_food_item'),
    path('foodadmin/food-items/<int:item_id>/delete/', admin_views.admin_delete_food_item, name='admin_delete_food_item'),
    path('foodadmin/food-items/<int:item_id>/toggle-featured/', admin_views.admin_toggle_featured, name='admin_toggle_featured'),
    path('foodadmin/food-items/<int:item_id>/toggle-available/', admin_views.admin_toggle_available, name='admin_toggle_available'),
    path('foodadmin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('foodadmin/categories/add/', admin_views.admin_add_category, name='admin_add_category'),
    path('foodadmin/categories/<int:cat_id>/edit/', admin_views.admin_edit_category, name='admin_edit_category'),
    path('foodadmin/categories/<int:cat_id>/delete/', admin_views.admin_delete_category, name='admin_delete_category'),
    path('foodadmin/customers/', admin_views.admin_customers, name='admin_customers'),
    path('foodadmin/shops/', admin_views.admin_shops, name='admin_shops'),
    path('foodadmin/agents/', admin_views.admin_agents, name='admin_agents'),
]
