from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import OfferSerializer
from .permissions import IsBusinessUser


class OfferCreateView(generics.CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsBusinessUser]
