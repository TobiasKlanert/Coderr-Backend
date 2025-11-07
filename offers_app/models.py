from django.db import models
from django.conf import settings


class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255, blank=True, default='')
    image = models.FileField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, default='')
    min_price = models.IntegerField(blank=True, default=0)
    min_delivery_time = models.IntegerField(blank=True, default=0)


class Detail(models.Model):
    offer = models.ForeignKey(
        Offer,
        related_name='details',
        on_delete=models.CASCADE
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
        default=OfferType.STANDARD
    )
