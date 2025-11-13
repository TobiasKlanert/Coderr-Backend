"""
offers_app.api.serializers
---------------------------------

Module summary
This module contains Django REST Framework serializers for the `offers_app`.
It defines three serializers:

- DetailSerializer: a lightweight model serializer for a single offer detail row.
- OfferCreateSerializer: used when creating an `Offer` together with exactly
    three `Detail` rows. It validates the details, enforces authentication via
    the request context, creates the Offer and its Detail objects, and updates
    cached summary fields (min price / min delivery time) on the Offer.
- OfferSerializer: read-only representation used for listing/retrieving offers.

Key behaviors & expectations
- Offer creation requires an authenticated user available in the serializer
    context under the `request` key (i.e. the view must pass `context={'request': request}`).
- The `OfferCreateSerializer` enforces that exactly three Detail objects are
    provided with distinct offer types: 'basic', 'standard', and 'premium'.
- The creation process calculates `min_price` and `min_delivery_time` from
    the created Detail instances and writes them to the Offer.

Error modes
- ValidationError is raised for missing authentication or invalid detail data.
- Any unexpected exception during creation is propagated as a 500 by DRF unless
    the caller catches it.
"""

from django.utils import timezone
from rest_framework import serializers
from ..models import Detail, Offer


class DetailSerializer(serializers.ModelSerializer):
    """Serializer for the Detail model.

    Fields serialized:
    - id
    - title
    - revisions
    - delivery_time_in_days
    - price
    - features
    - offer_type

    The `offer_type` field is exposed as a ChoiceField to ensure only the
    allowed enum values from `Detail.OfferType` are accepted.
    """

    offer_type = serializers.ChoiceField(choices=Detail.OfferType.choices)

    class Meta:
        model = Detail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]


class OfferCreateSerializer(serializers.ModelSerializer):
    """Serializer used for creating an Offer together with its Detail rows.

    Behaviour summary:
    - Accepts nested `details` (list of three Detail objects).
    - Validates that exactly three details are provided and that their
        `offer_type` values are the set {'basic', 'standard', 'premium'} exactly.
    - Requires an authenticated user in `self.context['request'].user` and
        associates the created Offer with that user.
    - Creates the Offer and the Detail instances, computes and updates the
        Offer's `min_price` and `min_delivery_time` cached fields, and returns
        the created Offer instance.

    Inputs (validated_data):
    - title, image, description (from the Offer model)
    - details: list of dicts representing Detail fields

    Errors:
    - Raises `serializers.ValidationError` if details count/types are invalid
        or if the user is not authenticated.
    """
    
    details = DetailSerializer(many=True)
    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]

    def validate_details(self, value):
        """Validate nested `details` payload.

        This method enforces two rules:
        1) The `details` value must be a list of exactly three items.
        2) The set of `offer_type` values across the three items must be
           exactly {'basic', 'standard', 'premium'} (no duplicates, no missing).

        Returns the validated list unchanged when valid.
        """

        if not isinstance(value, list) or len(value) != 3:
            raise serializers.ValidationError('An offer must contain exactly 3 details.')

        types = {item.get('offer_type') for item in value}
        required = {'basic', 'standard', 'premium'}
        if types != required:
            raise serializers.ValidationError('Details must include the types basic, standard, and premium (once each).')

        return value

    def create(self, validated_data):
        """Create an Offer and its nested Detail objects.

        Steps performed:
        1. Ensure `request` + authenticated user present in serializer context.
           Raises `serializers.ValidationError` if not authenticated.
        2. Pop `details` from validated_data and create the Offer instance
           associated with the authenticated user. The Offer's `updated_at`
           is set to the current time to avoid model defaults that may be
           incompatible with empty strings.
        3. Create three Detail objects linked to the Offer.
        4. Compute the minimum price and minimum delivery time across the
           created details and write those values back to the Offer's cached
           fields (`min_price`, `min_delivery_time`).

        Returns the created Offer instance.
        """

        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required.')

        details_data = validated_data.pop('details', [])

        # Ensure updated_at is valid on creation to avoid model default of ''
        offer = Offer.objects.create(
            user=request.user,
            updated_at=timezone.now(),
            **validated_data,
        )

        min_price = None
        min_delivery = None

        for item in details_data:
            detail = Detail.objects.create(offer=offer, **item)
            if min_price is None or detail.price < min_price:
                min_price = detail.price
            if min_delivery is None or detail.delivery_time_in_days < min_delivery:
                min_delivery = detail.delivery_time_in_days

        # Update cached fields
        offer.min_price = min_price or 0
        offer.min_delivery_time = min_delivery or 0
        try:
            offer.updated_at = timezone.now()
        except Exception:
            # Defensive: updated_at assignment should normally succeed
            pass
        offer.save(update_fields=['min_price', 'min_delivery_time', 'updated_at'])

        return offer


class OfferSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    user = serializers.IntegerField(source='user.id', read_only=True)
    user_details = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    """Read-only serializer for Offer instances.

    Fields included:
    - id, user (id), title, image, description
    - created_at, updated_at (ISO-like strings)
    - details: returns lightweight link objects for each Detail
    - min_price, min_delivery_time: cached summary values
    - user_details: small dict with basic information from the offer owner

    This serializer uses `get_details` to return compact link objects rather
    than nested Detail payloads, which keeps list endpoints lightweight.
    """

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        """Return a compact list representation of related Detail objects.

        Instead of embedding full Detail serializers, this method returns a
        list of small link objects that include the Detail `id` and a
        root-relative `url` to the detail endpoint. This keeps Offer list
        responses small and lets clients fetch full detail data only when
        needed.

        Returned format example:
        [ { 'id': 42, 'url': '/offerdetails/42/' }, ... ]
        """

        # Return lightweight link objects with root-level paths
        return [
            {
                'id': d.id,
                'url': f"/offerdetails/{d.id}/"
            }
            for d in obj.details.all()
        ]

    def get_user_details(self, obj):
        """Return a small dictionary with the Offer owner's public fields.

        This keeps the Offer representation self-contained for common UI
        scenarios where only a name and username are needed.
        """

        # Pull fields directly from the auth user (merged profile)
        u = obj.user
        return {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'username': u.username,
        }
