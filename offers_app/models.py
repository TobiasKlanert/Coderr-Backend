from django.db import models
from django.conf import settings


class Offer(models.Model):
    """
    Offer model representing a user's service or product offering.

    Attributes:
        user (django.db.models.ForeignKey):
            Reference to the user who created the offer. Uses settings.AUTH_USER_MODEL,
            cascades on delete, and is accessible via the related name 'offers'.
        title (str):
            Short, required title for the offer. CharField with max_length=255.
        image (File, optional):
            Optional uploaded file for the offer's image. Stored under 'offer_images/'.
            Field allows blank values and null in the database.
        description (str):
            Optional detailed description of the offer. TextField; may be blank.
        created_at (datetime):
            Timestamp set automatically when the offer is first created (auto_now_add=True).
        updated_at (datetime):
            Intended to track the last modification time.
        min_price (int):
            Required integer representing the minimum price for the offer. Defaults to 0.
        min_delivery_time (int):
            Required integer representing the minimum delivery time (units not specified).
            Defaults to 0.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255, blank=False, default='')
    image = models.FileField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    min_price = models.IntegerField(default=0)
    min_delivery_time = models.IntegerField(default=0)


class Detail(models.Model):
    """
    Detail model representing a single tier/option of an Offer.
    This model stores the information needed to describe one configurable offer
    detail/tier (for example: basic, standard, premium) that belongs to an Offer.
    Attributes
    ----------
    offer : ForeignKey
        Reference to the parent Offer (on_delete=models.CASCADE). Related name: 'details'.
    title : str
        Short human-readable title for the detail. Max length 255. Blank by default.
    revisions : int
        Number of revisions included. Defaults to 0.
    delivery_time_in_days : int
        Expected delivery time in days. Defaults to 0.
    price : int
        Price for this detail/tier (stored as integer, e.g. cents or whole units depending on app convention). Defaults to 0.
    features : list
        JSONField containing a list of feature descriptions (defaults to an empty list).
    offer_type : str
        Choice field specifying the tier type. Allowed values defined by OfferType:
        - 'basic'
        - 'standard' (default)
        - 'premium'
        Max length 8.
    Behavior and constraints
    ------------------------
    - Deleting the referenced Offer cascades and deletes associated Detail instances.
    - Persist features as JSON (list) to allow flexible, ordered feature items per tier.
    """
    offer = models.ForeignKey(
        Offer,
        related_name='details',
        on_delete=models.CASCADE
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
        default=OfferType.STANDARD
    )
