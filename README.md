# 🍽️ FoodieHub — Online Food Management System

A full-featured web-based food ordering and management system built with **Python** and **Django**.

---

## 📋 Features

### Customer Features
- User registration and login
- Browse food menu by category or search
- View detailed food item pages
- Add items to cart, update quantities
- Checkout with delivery details and payment method selection
- Order history and order status tracking
- User profile management

### Admin Features
- Full Django Admin panel
- Add / edit / delete food categories and items
- Mark items as featured, vegetarian, or unavailable
- View and update order statuses
- Manage customer accounts

---

## 🛠️ Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Backend     | Python 3.10+, Django 4.2           |
| Frontend    | HTML5, CSS3, Bootstrap 5, FontAwesome |
| Database    | SQLite (development) / PostgreSQL  |
| Auth        | Django built-in authentication     |
| Media       | Pillow (image handling)            |

---

## ⚡ Quick Setup

### 1. Clone / Extract the project
```bash
cd food_management_system
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Seed sample data (optional but recommended)
```bash
python seed_data.py
```
This creates:
- **Admin user:** `admin` / `admin123`
- **Demo user:** `customer` / `customer123`
- 8 categories and 28 food items

### 6. Run the development server
```bash
python manage.py runserver
```

Visit → **http://127.0.0.1:8000/**

---

## 📁 Project Structure

```
food_management_system/
├── manage.py
├── requirements.txt
├── seed_data.py
├── food_management/          # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── food_app/                 # Main application
    ├── models.py             # Database models
    ├── views.py              # View logic
    ├── urls.py               # URL routing
    ├── forms.py              # Django forms
    ├── admin.py              # Admin configuration
    ├── migrations/
    └── templates/food_app/
        ├── base.html
        ├── home.html
        ├── menu.html
        ├── food_detail.html
        ├── cart.html
        ├── checkout.html
        ├── order_detail.html
        ├── my_orders.html
        ├── profile.html
        ├── login.html
        └── register.html
```

---

## 🗄️ Database Models

| Model        | Description                                |
|--------------|--------------------------------------------|
| `Category`   | Food categories (e.g., Biryani, Pizza)     |
| `FoodItem`   | Individual food items with price & details |
| `Cart`       | Shopping cart (one per user)               |
| `CartItem`   | Items in the cart with quantities          |
| `Order`      | Customer orders with status tracking       |
| `OrderItem`  | Individual items in an order               |
| `UserProfile`| Extended user profile with address/phone   |

---

## 🔗 URL Routes

| URL                    | View               | Description              |
|------------------------|--------------------|--------------------------|
| `/`                    | `home`             | Landing page             |
| `/menu/`               | `menu`             | Browse all items         |
| `/menu/<id>/`          | `food_detail`      | Item detail page         |
| `/cart/`               | `cart`             | Shopping cart            |
| `/cart/add/<id>/`      | `add_to_cart`      | Add item to cart         |
| `/checkout/`           | `checkout`         | Place an order           |
| `/orders/`             | `my_orders`        | Order history            |
| `/orders/<id>/`        | `order_detail`     | Order confirmation       |
| `/profile/`            | `profile`          | User profile             |
| `/register/`           | `register_view`    | Register new account     |
| `/login/`              | `login_view`       | Login                    |
| `/logout/`             | `logout_view`      | Logout                   |
| `/admin/`              | Django Admin       | Admin panel              |

---

## 📸 Adding Food Images

1. Go to `/admin/` and log in as admin
2. Click on **Food Items** and edit any item
3. Upload an image in the **Image** field
4. Images are stored in the `media/food_items/` directory

---

## 🔒 Security Notes

- Change `SECRET_KEY` in `settings.py` before deploying
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` appropriately
- Use PostgreSQL and environment variables for production

---

## 📧 Contact

Built with ❤️ using Python & Django  
**Email:** info@foodiehub.com
