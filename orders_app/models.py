from django.db import models
from django.conf import settings


class Order(models.Model):
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

    title = models.CharField(max_length=255, blank=True, default='')
    revisions = models.IntegerField(blank=True, default=0)
    delivery_time_in_days = models.IntegerField(blank=True, default=0)
    price = models.IntegerField(blank=True, default=0)
    features = models.JSONField(default=list, blank=True)

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
