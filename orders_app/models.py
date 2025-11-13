"""
orders_app.models
------------------

Module summary
This module defines the `Order` model used to represent a customer order
created from an offer. The model stores references to both the customer and
business users, a small set of fields describing the ordered item (title,
revisions, delivery_time_in_days, price, features), an `offer_type` that
matches the offer tier, and a `status` to track order progress.

Primary responsibilities
- Persist orders placed between customers and businesses.
- Provide enum choices for `offer_type` and `status` to keep values
    consistent across the codebase.
"""

from django.db import models
from django.conf import settings


class Order(models.Model):
    """A persisted order created by a customer for a business.

    Fields
    - customer_user: FK to the user who requested the order (the customer).
    - business_user: FK to the user who will fulfill the order (the business).
    - title: short title or summary for the order.
    - revisions: integer number of allowed/used revisions for the order.
    - delivery_time_in_days: expected delivery time in whole days.
    - price: integer price (small codebase uses integer currency units).
    - features: JSON list holding free-form feature descriptions.
    - offer_type: one of 'basic', 'standard', 'premium' (see OfferType enum).
    - status: order workflow state (see Status enum).
    - created_at, updated_at: automatic timestamps for creation and modification.

    Behavior/constraints
    - Both `customer_user` and `business_user` use `on_delete=models.CASCADE`,
      meaning orders are removed if the referenced user is deleted.
    - `offer_type` and `status` are implemented as `TextChoices` enums to
      provide explicit allowed values and to make code checks clearer.

    Representation
    - `__str__` returns a short human-readable string: "Order #<id> - <title>".
    """

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_orders',
    )

    title = models.CharField(max_length=255, default='')
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    features = models.JSONField(default=list)

    class OfferType(models.TextChoices):
        BASIC = 'basic'
        STANDARD = 'standard'
        PREMIUM = 'premium'

    offer_type = models.CharField(
        max_length=8,
        choices=OfferType.choices,
        default=OfferType.STANDARD,
    )

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress'
        COMPLETED = 'completed'
        CANCELED = 'canceled'

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.title}"
