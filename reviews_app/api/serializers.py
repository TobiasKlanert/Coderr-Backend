from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Provides serialization and validation for creating and updating Review instances.
    Key behavior:
    - Subclasses serializers.ModelSerializer and maps model fields:
        - id
        - business_user
        - reviewer (read-only; set from request.user)
        - rating
        - description
        - created_at (read-only; formatted as '%Y-%m-%dT%H:%M:%SZ')
        - updated_at (read-only; formatted as '%Y-%m-%dT%H:%M:%SZ')
    - read_only_fields ensures 'reviewer', 'created_at', and 'updated_at' are not writable via input.
    Validation:
    - validate(self, attrs):
        - Obtains the current user from self.context['request'] and treats it as the reviewer.
        - Ensures a reviewer can only create one review per business_user by checking
          Review.objects.filter(reviewer=reviewer, business_user=business_user).
        - Raises serializers.ValidationError("You have already rated this user.") if a duplicate exists.
    Field access control on updates:
    - get_fields(self):
        - Inspects the request method (from self.context['request']).
        - Marks 'business_user' as read-only for PATCH and PUT requests to prevent changing the target user during updates.
    """
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
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
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and request.method in ['PATCH', 'PUT']:
            fields['business_user'].read_only = True

        return fields
