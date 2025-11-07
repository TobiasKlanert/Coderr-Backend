from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .serializers import OfferCreateSerializer, OfferListSerializer, DetailSerializer
from .permissions import IsBusinessUser
from ..models import Offer, Detail


class OfferListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        return OfferCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_queryset(self):
        return Offer.objects.all().distinct()


class DetailRetrieveView(generics.RetrieveAPIView):
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer
