from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OfferCreateSerializer, OfferListSerializer, DetailSerializer
from .permissions import IsBusinessUser
from ..models import Offer, Detail


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 12


class OfferListCreateView(generics.ListCreateAPIView):

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__id', 'min_price']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferListSerializer
        return OfferCreateSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_queryset(self):
        queryset = Offer.objects.all()

        time_param = self.request.query_params.get('max_delivery_time', None)
        if time_param is not None:
            max_days = int(time_param)
            queryset = queryset.filter(min_delivery_time__lte=max_days)

        return queryset


class DetailRetrieveView(generics.RetrieveAPIView):
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer
