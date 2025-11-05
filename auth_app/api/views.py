"""
API views for authentication-related endpoints.

This module exposes two class-based views:
- RegistrationView: allow anonymous users to register. Returns auth token and basic user info.
- CustomLoginView: allow anonymous users to log in using username + password. Returns auth token and user info.
"""

from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import RegistrationSerializer


class RegistrationView(APIView):
    """
    POST /registration/

    Permissions: AllowAny (anonymous users may create accounts)

    Request body: handled by RegistrationSerializer (username, email, password, repeated_password)

    Success response (201):
    {
        "token": "<auth token>",
        "username": "<username>",
        "email": "<email>",
        "user_id": <id>
    }

    Error response (400): serializer validation errors.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate incoming registration data
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Create user and a token for authentication
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)

            data = {
                'token': token.key,
                'username': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_201_CREATED)

        # Return serializer errors for invalid input
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    """
    POST /login/

    Permissions: AllowAny

    Request body: { "username": "...", "password": "..." } validated by standard serializer.

    Behavior:
    - Uses the serializer to authenticate (serializer adds 'user' to validated_data).
    - Returns or creates a Token for the authenticated user and returns basic user info.

    Success response (200):
    {
        "token": "<auth token>",
        "username": "<username>",
        "email": "<email>",
        "user_id": <id>
    }

    Errors:
    - 400 with serializer errors if credentials missing/invalid.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate credentials and authenticate via serializer
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        data = {
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }
        return Response(data)