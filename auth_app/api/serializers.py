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
        account = User(
            email=self.validated_data['email'], username=self.validated_data['username'])

        # Hash and set password, then persist
        account.set_password(pw)
        account.save()
        return account
