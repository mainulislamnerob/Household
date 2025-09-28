# 🏠 Household Service Providing Platform (DRF)

A **Django REST Framework (DRF)** based project that allows users to request and manage household services such as **House Shifting** and **Home Cleaning**.  
The platform supports two roles: **Admin** and **Client** with JWT authentication.  

---

## 🚀 Features

### 🔑 Authentication & Authorization
- Implemented **JWT Authentication** using [Djoser](https://djoser.readthedocs.io/)  
- Supports registration, login, logout, password reset, token refresh  

### 👑 Admin Features
- Promote users to **Admin** role  
- Manage users and services  
- Only Admins can create other Admins  

### 🙍‍♂️ Client Features
- Manage profile (bio, profile picture, social links)  
- View service history  
- Add/remove services from cart before placing order  

### 🛒 Services & Orders
- Add services to cart before placing an order  
- Place and manage orders  
- Order history with statuses (`pending`, `confirmed`, `completed`)  

### ⭐ Reviews & Ratings
- Clients can leave **ratings (1–5)** and reviews for services  
- Average rating is displayed per service  
- Services can be sorted by rating  

### 💳 Payments (Future Scope)
- Placeholder model for payment integration  
- Ready for integration with Stripe, PayPal, SSLCommerz  

### 📖 API Documentation
- Interactive API Docs with **Swagger UI** (`drf_yasg`)  
- Auto-generated schema at `/swagger/` and `/redoc/`  

---

## 🗂 Models Overview

- **User** → Custom user model with roles (Admin, Client), profile info  
- **Service** → Stores household services (title, description, price, rating)  
- **Cart / CartItem** → Manage cart items before checkout  
- **Order / OrderItem** → Stores orders with snapshot of service details  
- **Review** → Ratings & feedback for services  
- **PaymentIntent (placeholder)** → Future payment integration  

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework  
- **Authentication:** JWT (Djoser)  
- **API Docs:** drf_yasg (Swagger, Redoc)  
- **Database:** PostgreSQL (recommended) / SQLite (default)  
- **Deployment Ready:** Gunicorn, Docker (optional)  

---

## ⚙️ Installation & Setup

```bash
# Clone repository
git clone https://github.com/your-username/household-service-platform.git
cd household-service-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
