from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models import Order
from offers_app.models import Detail


class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.IntegerField(source='customer_user.id', read_only=True)
    business_user = serializers.IntegerField(source='business_user.id', read_only=True)

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
