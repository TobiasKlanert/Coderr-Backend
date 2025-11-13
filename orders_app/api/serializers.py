from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models import Order
from offers_app.models import Detail


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for representing Order instances in API responses.

    This Django REST Framework ModelSerializer serializes the Order model into a
    read-only representation suitable for list/detail endpoints. Key behaviors:

    - customer_user and business_user:
        - Exposed as IntegerFields sourced from the related user's `id` (source='customer_user.id'
          and source='business_user.id').
        - Both are read-only and return the primary key of the related user.

    - created_at and updated_at:
        - Exposed as DateTimeFields formatted as UTC timestamps in the form
          '%Y-%m-%dT%H:%M:%SZ' (ISO-like with trailing 'Z').
        - Both fields are read-only.

    - Fields included:
        - id, customer_user, business_user, title, revisions, delivery_time_in_days, price,
          features, offer_type, status, created_at, updated_at

    - Read-only behavior:
        - The serializer is configured so that all declared fields are read-only (read_only_fields
          equals the fields list). It is intended for serialization/representation only and not for
          creating or updating Order instances via incoming request data.
    """
    customer_user = serializers.IntegerField(source='customer_user.id', read_only=True)
    business_user = serializers.IntegerField(source='business_user.id', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating an Order from an existing Offer Detail.

    Fields
    - offer_detail_id (int): The primary key of the Detail (offer detail) to create the order from.
        This field must be provided in validated_data.

    Behavior
    - Expects a Django REST Framework request object in the serializer context under 'request'.
    - Ensures the request user is authenticated and uses that user as the order's customer_user.
    - Loads the referenced Detail using Detail.objects.select_related('offer', 'offer__user') to
        efficiently access the related Offer and its owner (business user).
    - On success, creates and returns a new Order instance populated from the Detail:
        - customer_user -> authenticated request user
        - business_user -> detail.offer.user
        - title, revisions, delivery_time_in_days, price, features, offer_type copied from Detail
        - status set to Order.Status.IN_PROGRESS

    Returns
    - Order: The created Order instance.

    Raises
    - serializers.ValidationError: If the request user is missing or not authenticated.
    - serializers.ValidationError: If a Detail with the given offer_detail_id does not exist.
    """
    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError({'detail': 'Authentication required.'})

        detail_id = validated_data.get('offer_detail_id')
        try:
            detail = Detail.objects.select_related('offer', 'offer__user').get(id=detail_id)
        except Detail.DoesNotExist:
            raise serializers.ValidationError({'offer_detail_id': 'Offer detail not found.'})

        order = Order.objects.create(
            customer_user=user,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
            status=Order.Status.IN_PROGRESS,
        )
        return order
