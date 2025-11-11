from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, attrs):
        request = self.context.get('request')
        reviewer = request.user
        business_user = attrs.get('business_user')

        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
            raise serializers.ValidationError(
                "You have already rated this user."
            )
        return attrs