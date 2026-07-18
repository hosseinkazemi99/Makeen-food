# Makeen Food API

A food ordering backend system built with **Django** and **Django REST Framework**.

Makeen Food is an API-based food ordering platform that provides separate functionalities for administrators and users.

The system allows administrators to manage foods and menus, while users can browse daily menus, create orders, manage their cart, use wallet services, and complete payments.

---

# Features

## Authentication

* Custom User Model
* JWT authentication
* Role-based permissions:

  * Admin users
  * Normal users
  * Authenticated users

---

# Admin Panel

The `admin_panel` application is responsible for system management.

Admin features:

* Create foods
* Update foods
* Upload food images
* Create daily menus
* Manage menu availability
* Soft delete foods and menus
* Create reports

Available reports:

* Order reports
* Financial reports

---

# User Panel

The `user_panel` application handles user operations.

User features:

* View available menus
* View food details
* Add items to cart
* Update cart items
* Remove cart items
* View current orders
* Manage wallet
* View wallet transactions
* Complete payments

---

# Payment System

The project contains a payment and wallet system.

## Wallet

Each user can have a wallet with:

* Balance management
* Deposit transactions
* Withdrawal transactions

## Payment

Payment records include:

* Order number
* Amount
* Transaction ID
* Payment status

Payment statuses:

```text
pending
success
failed
```

The project also supports a fake payment mode for development and testing.

Environment variable:

```env
USE_FAKE_PAYMENT=True
```

---

# Technologies

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* JWT Authentication
* Swagger / OpenAPI Documentation
* jdatetime (Jalali calendar support)

---

# Project Structure

```text
Makeen-food/
│
├── Food/
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── admin_panel/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
│
├── user_panel/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── media/
│   └── food images
│
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

# Main Models

## Food

Stores food information:

* Name
* Price
* Image
* Creation date
* Update date
* Soft delete status

## MenuModel

Represents food availability on specific dates.

Contains:

* Food
* Date
* Day of week
* Food price snapshot
* Available quantity
* Sold quantity

The price is stored in the menu to keep historical prices even if the food price changes later.

## UserModel

Custom user model containing:

* Username
* Name
* Rank
* Package
* Admin status

## Cart

Represents user's shopping cart.

Contains:

* User
* Payment status

## CartItem

Stores selected menu items:

* Menu
* Quantity
* Price

## Wallet

Stores user balance.

## Transaction

Records wallet operations:

* Deposit
* Withdrawal

## Payment

Stores payment information:

* User
* Amount
* Order number
* Transaction ID
* Payment status

---

# Environment Configuration

Create a `.env` file:

```env
SECRET_KEY=your-secret-key

DEBUG=True

POSTGRES_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

USE_FAKE_PAYMENT=True
```

---

# Run With Docker

Build and start the project:

```bash
docker compose up --build
```

The application will run on:

```text
http://localhost:8000
```

---

# Database

The project supports:

## Development

SQLite database:

```text
db.sqlite3
```

## Docker Environment

PostgreSQL database.

Database migrations are automatically applied when the container starts:

```bash
python manage.py migrate
```

---

# API Documentation

Swagger documentation is available through:

```text
/api/docs/
```

Example:

```text
http://localhost:8000/api/docs/
```

---

# Authentication Example

Login returns JWT tokens:

```json
{
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token"
}
```

Send token with requests:

```text
Authorization: Bearer <access_token>
```

---

# Development Notes

* Jalali date support implemented using `jdatetime`.
* Soft delete implemented using `on_deleted`.
* Menu stores food price snapshots to prevent historical price changes.
* Query optimization is handled using:

  * `select_related`
  * `prefetch_related`
* Serializers are based on Django REST Framework ModelSerializer where possible.

---

# Future Improvements

Possible improvements:

* Add automated tests
* Add production deployment using Gunicorn and Nginx
* Add Celery for background tasks
* Improve payment gateway abstraction
* Add order history management
* Add notifications

---

# License

This project is for learning and development purposes.
