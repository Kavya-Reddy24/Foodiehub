import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_management.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from food_app.models import (UserProfile, Shop, DeliveryAgent,
                              Category, FoodItem, Order, OrderTrackingLog)

# ── SUPERUSER ──────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@foodiehub.com', 'admin123',
                                          first_name='Admin', last_name='User')
    UserProfile.objects.create(user=admin, role='customer')
    print("✅ admin / admin123")

# ── SHOP MANAGERS ─────────────────────────────────────────────────
shops_data = [
    ('manager1', 'mgr1@foodiehub.com', 'mgr123', 'Rajesh', 'Kumar',
     'Spice Garden Restaurant',
     'Authentic Indian cuisine with rich flavours from every region of India.',
     '12, MG Road, Hyderabad - 500001, Telangana',
     '9876543210', 'spicegarden@foodiehub.com',
     'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80'),

    ('manager2', 'mgr2@foodiehub.com', 'mgr123', 'Priya', 'Reddy',
     'Pizza Palace',
     'Stone-baked artisan pizzas and Italian classics made fresh daily.',
     '45, Jubilee Hills, Hyderabad - 500033, Telangana',
     '9123456789', 'pizzapalace@foodiehub.com',
     'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&q=80'),
]

shops = {}
for uname, email, pwd, fn, ln, sname, sdesc, saddr, sphone, semail, simg in shops_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, pwd, first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='shop_manager', phone=sphone)
        shop = Shop.objects.create(manager=u, name=sname, description=sdesc,
                                   address=saddr, phone=sphone, email=semail,
                                   image_url=simg)
        shops[uname] = shop
        print(f"✅ Shop: {sname} (manager: {uname} / {pwd})")
    else:
        shops[uname] = Shop.objects.get(manager__username=uname)

# ── DELIVERY AGENTS ───────────────────────────────────────────────
agents_data = [
    ('agent1', 'agent1@foodiehub.com', 'agt123', 'Arjun', 'Singh', 'Honda Activa - TS09AB1234'),
    ('agent2', 'agent2@foodiehub.com', 'agt123', 'Suresh', 'Babu',  'Royal Enfield - TS07CD5678'),
]
for uname, email, pwd, fn, ln, vehicle in agents_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, pwd, first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='delivery_agent', phone='9000000000')
        DeliveryAgent.objects.create(user=u, vehicle=vehicle, status='available')
        print(f"✅ Agent: {fn} {ln} (login: {uname} / {pwd})")

# ── DEMO CUSTOMER ─────────────────────────────────────────────────
if not User.objects.filter(username='customer').exists():
    cu = User.objects.create_user('customer', 'customer@example.com', 'customer123',
                                   first_name='John', last_name='Doe')
    UserProfile.objects.create(user=cu, role='customer', phone='9876543210',
                                address='123 Main Street, Hyderabad - 500001')
    print("✅ customer / customer123")

# ── CATEGORIES ────────────────────────────────────────────────────
categories_data = [
    ('Starters',     'Crispy and delicious starters',      'https://images.unsplash.com/photo-1541014741259-de529411b96a?w=400&q=80'),
    ('Main Course',  'Hearty main course meals',            'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),
    ('Biryani',      'Aromatic rice dishes',                'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80'),
    ('Desserts',     'Sweet treats and desserts',           'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&q=80'),
    ('Beverages',    'Refreshing drinks',                   'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&q=80'),
    ('Pizza',        'Wood-fired pizzas',                   'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&q=80'),
    ('Burgers',      'Juicy burgers',                       'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80'),
    ('South Indian', 'Authentic South Indian cuisine',      'https://images.unsplash.com/photo-1630383249896-424e482df921?w=400&q=80'),
]
cats = {}
for name, desc, img in categories_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'image_url': img})
    cats[name] = cat

# ── FOOD ITEMS with shop & unique item_code ────────────────────────
# (name, desc, price, cat, is_veg, is_featured, img, shop_key)
items_data = [
    # Spice Garden
    ('Veg Spring Rolls', 'Crispy golden rolls stuffed with fresh vegetables.', 120, 'Starters', True, True,
     'https://images.unsplash.com/photo-1515669097368-22e68427d265?w=500&q=80', 'manager1'),
    ('Chicken Tikka', 'Marinated chicken grilled in a tandoor until perfectly charred.', 220, 'Starters', False, True,
     'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=500&q=80', 'manager1'),
    ('Paneer Tikka', 'Cottage cheese marinated and grilled with peppers and onions.', 180, 'Starters', True, True,
     'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=500&q=80', 'manager1'),
    ('Butter Chicken', 'Tender chicken in a velvety tomato-butter gravy.', 280, 'Main Course', False, True,
     'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=500&q=80', 'manager1'),
    ('Paneer Butter Masala', 'Cottage cheese in rich creamy tomato gravy.', 240, 'Main Course', True, True,
     'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=500&q=80', 'manager1'),
    ('Dal Makhani', 'Slow-cooked black lentils with butter and cream.', 180, 'Main Course', True, False,
     'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=500&q=80', 'manager1'),
    ('Chicken Biryani', 'Fragrant basmati layered with spiced chicken and saffron.', 320, 'Biryani', False, True,
     'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&q=80', 'manager1'),
    ('Veg Biryani', 'Garden-fresh vegetables with aromatic basmati rice.', 240, 'Biryani', True, True,
     'https://images.unsplash.com/photo-1645177628172-a94c1f96debb?w=500&q=80', 'manager1'),
    ('Mutton Biryani', 'Slow-cooked mutton dum biryani with fragrant basmati.', 380, 'Biryani', False, False,
     'https://images.unsplash.com/photo-1599043513900-ed6fe01d3833?w=500&q=80', 'manager1'),
    ('Masala Dosa', 'Crispy crepe filled with spiced potato masala.', 120, 'South Indian', True, True,
     'https://images.unsplash.com/photo-1630383249896-424e482df921?w=500&q=80', 'manager1'),
    ('Idli Sambar', 'Steamed rice cakes with sambar and coconut chutney.', 90, 'South Indian', True, False,
     'https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=500&q=80', 'manager1'),
    ('Vada', 'Crispy lentil donuts served with coconut chutney.', 80, 'South Indian', True, False,
     'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=500&q=80', 'manager1'),
    ('Gulab Jamun', 'Milk dumplings soaked in rose and cardamom syrup.', 80, 'Desserts', True, False,
     'https://images.unsplash.com/photo-1666195596782-b85ce0d5ce44?w=500&q=80', 'manager1'),
    ('Mango Lassi', 'Thick Alphonso mango blended with yoghurt.', 80, 'Beverages', True, True,
     'https://images.unsplash.com/photo-1527324688151-0e627063f2b1?w=500&q=80', 'manager1'),
    ('Fresh Lime Soda', 'Zesty lime juice topped with chilled soda.', 60, 'Beverages', True, False,
     'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&q=80', 'manager1'),

    # Pizza Palace
    ('Margherita Pizza', 'Classic tomato sauce, fresh mozzarella and basil.', 240, 'Pizza', True, True,
     'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=500&q=80', 'manager2'),
    ('Chicken BBQ Pizza', 'Smoky BBQ chicken, peppers and mozzarella.', 320, 'Pizza', False, True,
     'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=500&q=80', 'manager2'),
    ('Veggie Supreme Pizza', 'Roasted vegetables, mushrooms and olives.', 280, 'Pizza', True, False,
     'https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?w=500&q=80', 'manager2'),
    ('Classic Beef Burger', 'Flame-grilled beef patty with lettuce, tomato and pickles.', 180, 'Burgers', False, True,
     'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&q=80', 'manager2'),
    ('Aloo Tikki Burger', 'Spiced potato tikki with green chutney in a soft bun.', 120, 'Burgers', True, False,
     'https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=500&q=80', 'manager2'),
    ('Chicken Zinger Burger', 'Crispy chicken fillet with coleslaw and spicy mayo.', 160, 'Burgers', False, False,
     'https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=500&q=80', 'manager2'),
    ('Ice Cream', 'Creamy handcrafted ice cream in three classic flavours.', 100, 'Desserts', True, False,
     'https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=500&q=80', 'manager2'),
    ('Cold Coffee', 'Brewed coffee blended with milk and vanilla ice cream.', 100, 'Beverages', True, False,
     'https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=500&q=80', 'manager2'),
    ('Uttapam', 'Thick soft rice pancake topped with onions and tomatoes.', 110, 'South Indian', True, False,
     'https://images.unsplash.com/photo-1694489555741-03d30e5adfd6?w=500&q=80', 'manager2'),
    ('Palak Paneer', 'Cottage cheese in fresh spinach gravy with garlic.', 220, 'Main Course', True, False,
     'https://images.unsplash.com/photo-1604152135912-04a022e23696?w=500&q=80', 'manager2'),
    ('Chicken Curry', 'Bold home-style chicken curry with whole spices.', 260, 'Main Course', False, False,
     'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=500&q=80', 'manager2'),
    ('Rasgulla', 'Spongy paneer balls in light sugar syrup.', 90, 'Desserts', True, False,
     'https://images.unsplash.com/photo-1601303516534-bf1ff41ec4b3?w=500&q=80', 'manager2'),
    ('Mushroom Manchurian', 'Crispy mushrooms tossed in spicy Manchurian sauce.', 160, 'Starters', True, False,
     'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500&q=80', 'manager2'),
]

count = 0
for name, desc, price, cat_name, is_veg, is_feat, img, shop_key in items_data:
    shop_obj = shops.get(shop_key)
    item, created = FoodItem.objects.get_or_create(
        name=name,
        defaults={'description': desc, 'price': price, 'category': cats[cat_name],
                  'is_vegetarian': is_veg, 'is_featured': is_feat,
                  'is_available': True, 'image_url': img, 'shop': shop_obj}
    )
    if not created:
        item.image_url = img; item.shop = shop_obj; item.save()
    count += 1

print(f"✅ {count} food items seeded")
print("\n🎉 Database seeded!")
print("🔑 admin / admin123  |  manager1 / mgr123  |  manager2 / mgr123")
print("🔑 agent1 / agt123   |  agent2 / agt123    |  customer / customer123")
print("🌐 http://127.0.0.1:8000/   |  Admin: http://127.0.0.1:8000/foodadmin/")
