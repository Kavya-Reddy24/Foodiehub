import uuid
from django.db import models
from django.contrib.auth.models import User


# ── ROLE CHOICES ──────────────────────────────────────────────────
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('customer',        'Customer'),
        ('shop_manager',    'Shop Manager'),
        ('delivery_agent',  'Delivery Agent'),
    ]
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role    = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone   = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_shop_manager(self):
        return self.role == 'shop_manager'

    def is_delivery_agent(self):
        return self.role == 'delivery_agent'


# ── SHOP ──────────────────────────────────────────────────────────
class Shop(models.Model):
    manager     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address     = models.TextField()
    phone       = models.CharField(max_length=15, blank=True)
    email       = models.EmailField(blank=True)
    image_url   = models.URLField(blank=True, default='')
    is_open     = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def avg_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0.0


# ── CATEGORY ──────────────────────────────────────────────────────
class Category(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url   = models.URLField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


# ── FOOD ITEM ─────────────────────────────────────────────────────
class FoodItem(models.Model):
    # Unique menu item ID (e.g. FH-0001)
    item_code    = models.CharField(max_length=20, unique=True, blank=True)
    shop         = models.ForeignKey(Shop, on_delete=models.CASCADE,
                                     related_name='food_items', null=True, blank=True)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE,
                                     related_name='food_items')
    name         = models.CharField(max_length=200)
    description  = models.TextField()
    price        = models.DecimalField(max_digits=8, decimal_places=2)
    image        = models.ImageField(upload_to='food_items/', blank=True, null=True)
    image_url    = models.URLField(blank=True, default='')
    is_available = models.BooleanField(default=True)
    is_vegetarian= models.BooleanField(default=False)
    is_featured  = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.item_code:
            # Auto-generate FH-XXXX code
            last = FoodItem.objects.order_by('id').last()
            next_id = (last.id + 1) if last else 1
            self.item_code = f'FH-{next_id:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.item_code}] {self.name}'


# ── DELIVERY AGENT ────────────────────────────────────────────────
class DeliveryAgent(models.Model):
    STATUS_CHOICES = [
        ('available',   'Available'),
        ('on_delivery', 'On Delivery'),
        ('offline',     'Offline'),
    ]
    user       = models.OneToOneField(User, on_delete=models.CASCADE,
                                       related_name='delivery_agent')
    vehicle    = models.CharField(max_length=100, blank=True,
                                  help_text='e.g. Honda Activa - KA05AB1234')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                  default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.status})'


# ── CART ──────────────────────────────────────────────────────────
class Cart(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total(self):
        return sum(item.get_subtotal() for item in self.cart_items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.cart_items.all())


class CartItem(models.Model):
    cart      = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

    def get_subtotal(self):
        return self.food_item.price * self.quantity


# ── ORDER ─────────────────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',          'Order Placed'),
        ('shop_accepted',    'Shop Accepted'),
        ('preparing',        'Being Prepared'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('agent_assigned',   'Delivery Agent Assigned'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',        'Delivered'),
        ('cancelled',        'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi',  'UPI'),
    ]

    user               = models.ForeignKey(User, on_delete=models.CASCADE,
                                            related_name='orders')
    shop               = models.ForeignKey(Shop, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='orders')
    delivery_agent     = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='orders')
    status             = models.CharField(max_length=25, choices=STATUS_CHOICES,
                                          default='pending')
    payment_method     = models.CharField(max_length=20, choices=PAYMENT_CHOICES,
                                          default='cash')
    payment_status     = models.BooleanField(default=False)
    total_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address   = models.TextField()
    phone_number       = models.CharField(max_length=15)
    special_instructions = models.TextField(blank=True)

    # Timestamps per stage
    shop_accepted_at   = models.DateTimeField(null=True, blank=True)
    agent_assigned_at  = models.DateTimeField(null=True, blank=True)
    delivered_at       = models.DateTimeField(null=True, blank=True)

    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE,
                                   related_name='order_items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField()
    price     = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name}"

    def get_subtotal(self):
        return self.price * self.quantity


# ── ORDER TRACKING LOG ────────────────────────────────────────────
class OrderTrackingLog(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE,
                                   related_name='tracking_logs')
    status    = models.CharField(max_length=25)
    message   = models.CharField(max_length=255)
    actor     = models.ForeignKey(User, on_delete=models.SET_NULL,
                                   null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'Order#{self.order.id} → {self.status}'
