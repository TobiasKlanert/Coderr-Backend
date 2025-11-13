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
from .serializers import RegistrationSerializer, UserDetailSerializer, UserListSerializer
from ..models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics


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


class UserProfileRetrieveView(APIView):
    """GET a specific user's public profile details by user id (pk)."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        data = UserDetailSerializer(user).data
        # Ensure non-null string fields come as empty strings
        for f in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(f) is None:
                data[f] = ""
        return Response(data)

    def patch(self, request, pk):
        # 401 if not authenticated
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # 404 if user not found
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        # 403 if not owner
        if request.user.id != user.id:
            return Response({"detail": "You can only edit your own profile."}, status=status.HTTP_403_FORBIDDEN)

        # Update allowed fields
        try:
            update_fields = [
                ("first_name", True),
                ("last_name", True),
                ("location", True),
                ("tel", True),
                ("description", True),
                ("working_hours", True),
                ("email", False),
            ]

            for field, empty_to_blank in update_fields:
                if field in request.data:
                    val = request.data.get(field)
                    if empty_to_blank and (val is None):
                        val = ""
                    setattr(user, field, val or ("" if empty_to_blank else val))

            # Ensure email uniqueness when updating
            if "email" in request.data:
                new_email = request.data.get("email") or ""
                if new_email and User.objects.exclude(pk=user.pk).filter(email=new_email).exists():
                    return Response({"email": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

            user.save()

            data = UserDetailSerializer(user).data
            for f in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
                if data.get(f) is None:
                    data[f] = ""
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BusinessProfilesListView(generics.ListAPIView):
    """
    List API view that returns all user profiles of type BUSINESS.

    This view is a DRF generics.ListAPIView configured to use UserListSerializer
    and requires the requesting user to be authenticated (IsAuthenticated).

    Behavior:
    - get_queryset() returns a Django QuerySet of User instances filtered where
        User.type == User.Type.BUSINESS and ensures distinct results.
    - Any exception raised during queryset construction is intentionally allowed
        to propagate so that DRF will convert it into a 500 response.

    HTTP semantics:
    - Method: GET
    - Success: 200 OK with a paginated list of serialized business user objects
        (pagination, filtering, and ordering are applied if enabled in the DRF settings
        or via additional view attributes).
    - Authentication failure: 401 Unauthorized (when the request is unauthenticated).
    - Server error: 500 Internal Server Error if an unexpected exception occurs.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            return User.objects.filter(type=User.Type.BUSINESS).distinct()
        except Exception:
            # Bubble up to DRF -> 500
            raise


class CustomerProfilesListView(generics.ListAPIView):
    """ 
    List API view that returns all user profiles of type CUSTOMER.
    """
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            return User.objects.filter(type=User.Type.CUSTOMER).distinct()
        except Exception:
            # Bubble up to DRF -> 500
            raise
