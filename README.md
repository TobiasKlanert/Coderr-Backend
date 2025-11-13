# Coderr Backend (Django + DRF)

Coderr is a multi-tenant marketplace backend for connecting customers with business partners. The service is built with Django 5.2 and Django REST Framework (DRF) and exposes token-secured endpoints for authentication, offer management, ordering, reviews, and lightweight dashboard metrics. This document summarizes everything you need to run and extend the project locally and to present it on GitHub.

## Features
- Custom `auth_app.User` model with business/customer roles, extended profile fields, and token-based auth.
- Offer lifecycle: business accounts create offers that must contain exactly three priced tiers (basic/standard/premium).
- Customers convert offer tiers into orders and track progress via status updates handled by business owners.
- Review system with one-review-per-customer-per-business enforcement and filtering/search helpers.
- Dashboard endpoint for aggregated KPIs (counts and average rating) plus dedicated order counters for business profiles.
- Filtered, searchable, and paginated listings powered by `django-filter`, DRF ordering/search filters, and custom pagination defaults.

## Tech stack
- Python, Django 5, Django REST Framework
- Django Filter
- SQLite by default (easy local dev)
- Token Authentication (`rest_framework.authtoken`)
- CORS support for a frontend (defaults to `http://127.0.0.1:5500`)

## Requirements

- Python 3.10+ (3.11 recommended)
- pip / venv

## Getting Started (Local)

### 1) Clone and enter the project directory

```
git clone https://github.com/TobiasKlanert/Coderr-Backend.git
cd Coderr-Backend
```

### 2) Create and activate a virtual environment

```
python -m venv env
# Windows
.\env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

### 3) Install dependencies

```
pip install -r requirements.txt
```

### 4) Apply database migrations

```
python manage.py migrate
```

### 5) (Optional) Create an admin user to access `/admin/`

```
python manage.py createsuperuser
```

### 6) Run the development server

```
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Configuration

All settings live in `core/settings.py`.

- `SECRET_KEY`: Currently hardcoded for development. For production, set this from an environment variable and keep it secret.
- `DEBUG`: Set to `True` for development. Must be `False` in production.
- `ALLOWED_HOSTS`: Add your domain(s) or IPs for production.
- `DATABASES`: Uses SQLite by default. Switch to Postgres/MySQL for production.
- `CORS_ALLOWED_ORIGINS`: Add your frontend origin(s). Defaults to `http://127.0.0.1:5500`.
- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`: Uses Token Authentication.

Note: The project does not currently read a `.env` file. If you want environment‑based config, integrate a package like `django-environ` and update `core/settings.py` accordingly.

## Authentication flow
1. **Register** (`POST /api/registration/`) with `username`, `email`, `password`, `repeated_password`, and `type` (`customer` or `business`). Response returns a token.
2. **Login** (`POST /api/login/`) with username/password to retrieve an auth token if you already have an account.
3. **Use the token** on every authenticated request:
   ```
   Authorization: Token <token-from-registration-or-login>
   ```

Example: log in and fetch your profile.
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"secret"}'

curl http://127.0.0.1:8000/api/profile/1/ \
  -H "Authorization: Token <token>"
```

## API overview

### Auth & profiles (`auth_app`)

| Endpoint | Method(s) | Description | Auth |
| --- | --- | --- | --- |
| `/api/registration/` | POST | Register a new user (customer/business). Returns token + user info. | AllowAny |
| `/api/login/` | POST | Obtain token via username/password. | AllowAny |
| `/api/profile/<id>/` | GET | Public profile view with normalized fields. | AllowAny |
| `/api/profile/<id>/` | PATCH | Update own profile (`first_name`, `last_name`, contact info, etc.). | Token + owner only |
| `/api/profiles/business/` | GET | List all business profiles. | Token |
| `/api/profiles/customer/` | GET | List all customer profiles. | Token |

### Offers (`offers_app`)

| Endpoint | Method(s) | Description | Auth |
| --- | --- | --- | --- |
| `/api/offers/` | GET | Public, paginated offer list with filtering (`user__id`, `min_price`), `max_delivery_time` query param, search (title/description), ordering (`updated_at`, `min_price`). Page size defaults to 6. | AllowAny |
| `/api/offers/` | POST | Create a new offer with **exactly three** nested detail tiers (basic/standard/premium). Automatically sets `min_price` and `min_delivery_time`. | Token + business |
| `/api/offers/<id>/` | GET | Retrieve a single offer with user info and detail URLs. | Token |
| `/api/offers/<id>/` | PATCH | Update offer scalar fields or replace detail records. Only the offer owner may edit. | Token + owner |
| `/api/offers/<id>/` | DELETE | Remove an offer. Owner-only. | Token + owner |
| `/api/offerdetails/<detail_id>/` | GET | Fetch a full `Detail` object (title, price, features, etc.). | Token |

### Orders (`orders_app`)

| Endpoint | Method(s) | Description | Auth |
| --- | --- | --- | --- |
| `/api/orders/` | GET | List orders for the current user. Customers see their purchases; business users see orders assigned to them. Ordered by `-created_at`. | Token |
| `/api/orders/` | POST | Customers create an order from an offer detail via `{"offer_detail_id": <id>}`. Copies the tier snapshot into the new order. | Token + customer |
| `/api/orders/<id>` | GET | Retrieve order details. | Token |
| `/api/orders/<id>` | PATCH | Business owner updates order `status` (`in_progress`, `completed`, `canceled`). | Token + business owner |
| `/api/orders/<id>` | DELETE | Admin-only hard delete. | Token + admin |
| `/api/order-count/<business_id>/` | GET | Count `in_progress` orders for a business profile. | Token |
| `/api/completed-order-count/<business_id>/` | GET | Count completed orders for a business profile. | Token |

### Reviews (`reviews_app`)

| Endpoint | Method(s) | Description | Auth |
| --- | --- | --- | --- |
| `/api/reviews/` | GET | List reviews with filtering (`business_user_id`, `reviewer_id`), ordering (`updated_at`, `rating`), and search support. | Token |
| `/api/reviews/` | POST | Customers create a review; serializer enforces a single review per (customer, business) pair. `reviewer` auto-populates from the token. | Token + customer |
| `/api/reviews/<id>/` | GET | Retrieve review detail. | Token |
| `/api/reviews/<id>/` | PATCH | Reviewer updates their own review; timestamps set via `timezone.now()`. | Token + reviewer |
| `/api/reviews/<id>/` | DELETE | Reviewer-only delete. | Token + reviewer |

### Dashboard (`dashboard_app`)

| Endpoint | Method(s) | Description | Auth |
| --- | --- | --- | --- |
| `/api/base-info/` | GET | Public dashboard metrics: total reviews, averaged rating (1 decimal), business profile count, and total offers. | AllowAny |

## Domain rules & special cases
- **Offer creation** demands three distinct tiers labelled `basic`, `standard`, `premium`. Missing or duplicated tiers raise a validation error.
- **Offer ownership**: Updates, deletes, and nested detail modifications require the request user to match `offer.user`. Business type is not enough.
- **Orders**: Only customers can create orders, and they must reference a valid `offers_app.Detail`. Business owners alone can change statuses via `PATCH`.
- **Order statistics** endpoints guard that the provided user is of type `business`; otherwise they 404.
- **Reviews**: Only customers may create them. `ReviewSerializer` prohibits duplicate reviews per business, and the `IsReviewer` permission ensures only the reviewer can mutate or delete.
- **Profiles**: `UserProfileRetrieveView` lets anyone read but restricts `PATCH` to the owner, with uniqueness validation on email updates.
- **Dashboard & order counters** power the client UI; caching layers are not in place, so consider database load when scaling.
- **Media uploads** use `FileField`, so Pillow is unnecessary unless you switch to `ImageField`. Files land under `media/profile_pictures/` and `media/offer_images/`.

## Sample workflows

### Create an offer (business user)
```bash
curl -X POST http://127.0.0.1:8000/api/offers/ \
  -H "Authorization: Token <business-token>" \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Brand identity packages",
        "description": "Flexible branding tiers.",
        "details": [
          {"title":"Basic","revisions":1,"delivery_time_in_days":7,"price":900,"features":["Logo"],"offer_type":"basic"},
          {"title":"Standard","revisions":2,"delivery_time_in_days":14,"price":1500,"features":["Logo","Guidelines"],"offer_type":"standard"},
          {"title":"Premium","revisions":3,"delivery_time_in_days":21,"price":2200,"features":["Logo","Guidelines","Stationery"],"offer_type":"premium"}
        ]
      }'
```

### Place an order (customer)
```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Authorization: Token <customer-token>" \
  -H "Content-Type: application/json" \
  -d '{"offer_detail_id": 12}'
```
The API copies the referenced detail into an `Order`, assigning `business_user` from the parent offer and setting status to `in_progress`.

### Leave a review
```bash
curl -X POST http://127.0.0.1:8000/api/reviews/ \
  -H "Authorization: Token <customer-token>" \
  -H "Content-Type: application/json" \
  -d '{"business_user": 7, "rating": 5, "description": "Amazing quality!"}'
```
Trying to review the same business twice raises `{"non_field_errors":["You have already rated this user."]}`.

## Media & static assets
- Uploaded files are served from `/media/` thanks to `django.conf.urls.static` when `DEBUG=True`. Configure your production web server (NGINX/S3/etc.) to serve `MEDIA_ROOT`.
- Run `python manage.py collectstatic --noinput` before deploying with `DEBUG=0` so static files are gathered in `STATIC_ROOT`.

## Deployment checklist
1. Set `DEBUG=False`, configure `ALLOWED_HOSTS`, and provide a secure `SECRET_KEY`.
2. Switch to a managed database (PostgreSQL recommended) and migrate.
3. Configure HTTPS and CSRF trusted origins for your domain.
4. Serve static/media files via the web server or object storage.
5. Rotate tokens or enable HTTPS-only transport for auth.
6. Consider adding caching (Redis) or task queues if offer/order volume grows.

## Troubleshooting
- **401 Unauthorized**: Verify the `Authorization: Token ...` header and that the token is issued to the correct user type.
- **403 Forbidden when creating offers**: The authenticated user must have `type="business"`.
- **Offer creation errors about details**: Ensure your payload has exactly three items with `offer_type` values of `basic`, `standard`, and `premium`.
- **Email already exists**: The profile update and registration flows enforce unique emails; update with a different one or remove the conflicting user.
- **Order PATCH rejected**: Only the `business_user` tied to the order can update its status, and the value must be one of `in_progress`, `completed`, or `canceled`.
- **Static/media 404s in production**: Django only serves `/media/` when `DEBUG=True`; configure your web server or object storage to handle these paths.

---

Need help or have ideas for improvements? Open an issue or start a discussion in the repository. Happy coding!
