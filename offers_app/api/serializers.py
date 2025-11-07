from django.utils import timezone
from rest_framework import serializers
from ..models import Detail, Offer
from profile_app.models import UserProfile


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


class OfferSerializer(serializers.ModelSerializer):
    details = DetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

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

        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist: 
            raise serializers.ValidationError('No user profile found.')

        details_data = validated_data.pop('details', [])

        # Ensure updated_at is valid on creation to avoid model default of ''
        offer = Offer.objects.create(
            user=user_profile,
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
