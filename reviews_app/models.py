from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Model representing a review left by a customer for a business user.

    Fields
    - business_user (ForeignKey): The user who is the subject of the review (the business). Deleting the user cascades and removes related reviews.
    - reviewer (ForeignKey): The user who created the review. Deleting the reviewer cascades and removes related reviews.
    - rating (int): Integer rating constrained to the range 0–5 (inclusive) via MinValueValidator and MaxValueValidator.
    - description (str): Optional textual details of the review. Blank by default and defaults to an empty string.
    - created_at (datetime): Timestamp automatically set when the review is first created.
    - updated_at (datetime): Timestamp intended to record the last update time. (Note: typically this should use auto_now=True so it updates on each save.)

    Behavior and constraints
    - rating must be an integer between 0 and 5 inclusive.
    - Both business_user and reviewer reference the configured AUTH_USER_MODEL; consider enforcing that they are not the same user if self-reviews are disallowed.
    - Deleting either referenced user will delete associated reviews due to on_delete=models.CASCADE.
    """
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_user'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviewer'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
