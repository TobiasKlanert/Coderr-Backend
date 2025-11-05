"""
Custom User model extending Django's AbstractUser.

This model introduces a 'type' field to classify users as either a customer
or a business. It provides a small set of choices via the nested Type
TextChoices class and defaults to the CUSTOMER type.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Attributes:
        type (str): A CharField (max_length=8) storing the user category. Valid
            values are defined by Type (Type.CUSTOMER = 'customer',
            Type.BUSINESS = 'business'). Defaults to Type.CUSTOMER.
    Inner classes:
        Type: A TextChoices enumeration providing the allowed values for the
            'type' field: CUSTOMER and BUSINESS.
    Methods:
        __str__(): Returns a human-readable representation of the user (the
            username).
    """
    class Type(models.TextChoices):
        CUSTOMER = 'customer'
        BUSINESS = 'business'

    type = models.CharField(
        max_length=8,
        choices=Type.choices,
        default=Type.CUSTOMER
    )

    def __str__(self):
        return self.email or self.username
