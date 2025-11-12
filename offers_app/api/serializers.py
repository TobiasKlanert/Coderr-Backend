from django.utils import timezone
from rest_framework import serializers
from ..models import Detail, Offer


class DetailSerializer(serializers.ModelSerializer):
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
    details = DetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'title', 'image', 'description', 'details'
        ]

    def validate_details(self, value):
        if not isinstance(value, list) or len(value) != 3:
            raise serializers.ValidationError('An offer must contain exactly 3 details.')

        types = {item.get('offer_type') for item in value}
        required = {'basic', 'standard', 'premium'}
        if types != required:
            raise serializers.ValidationError('Details must include the types basic, standard, and premium (once each).')

        return value

    def create(self, validated_data):
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
            pass
        offer.save(update_fields=['min_price', 'min_delivery_time', 'updated_at'])

        return offer


class OfferSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    user = serializers.IntegerField(source='user.id', read_only=True)
    user_details = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_details(self, obj):
        # Return lightweight link objects with root-level paths
        return [
            {
                'id': d.id,
                'url': f"/offerdetails/{d.id}/"
            }
            for d in obj.details.all()
        ]

    def get_user_details(self, obj):
        # Pull fields directly from the auth user (merged profile)
        u = obj.user
        return {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'username': u.username,
        }
