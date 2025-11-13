"""
Serializers for the authentication API.

This module defines:
- RegistrationSerializer: validates registration data and creates a new User.

"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from ..models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Fields:
    - username: displayed username
    - email: user's email address (unique)
    - password: write-only password
    - repeated_password: write-only confirmation password
    - type: type of user (customer or business)

    Behavior:
    - Validates that password and repeated_password match.
    - Ensures the email is not already registered.
    - Creates a User instance, hashes the password with set_password, and saves it.
    """
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'type': {
                'write_only': True
            }
        }

    def save(self):
        """
        Create and return a new User from validated_data.

        Raises:
            serializers.ValidationError: if passwords don't match or email already exists.

        Returns:
            User: newly created user instance.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']

        # Ensure the two password entries match
        if pw != repeated_pw:
            raise serializers.ValidationError(
                {'error': 'passwords dont match'})

        # Ensure email uniqueness
        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({
                "email": "Email already exists"
            })

        # Create new user
        user_type = self.validated_data.get('type', User.Type.CUSTOMER)
        account = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            type=user_type,
        )

        # Hash and set password, then persist
        account.set_password(pw)
        account.save()

        return account


class UserDetailSerializer(serializers.ModelSerializer):
    """Read-only serializer for user profile details."""
    created_at = serializers.DateTimeField(source='date_joined', format='%Y-%m-%dT%H:%M:%SZ', read_only=True)
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at',
        ]
        read_only_fields = fields


class UserListSerializer(serializers.ModelSerializer):
    """List serializer for public user profile info (business/customer lists)."""
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]
        read_only_fields = fields

    def to_representation(self, instance):
        """
        Return a serialized representation of `instance`, normalizing select fields.

        This method obtains the base representation by calling the parent serializer's
        to_representation and then ensures that the following fields are always present
        as empty strings rather than None: "first_name", "last_name", "location",
        "tel", "description", and "working_hours". If any of these keys are missing
        or have a value of None in the base representation, they are set to "".
        All other fields returned by the parent representation are left unchanged.

        Args:
            instance: The model instance (or object) to be serialized.

        Returns:
            dict: A dictionary representation of `instance` with specified None values
            replaced by empty strings.
        """
        data = super().to_representation(instance)
        for f in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(f) is None:
                data[f] = ""
        return data
