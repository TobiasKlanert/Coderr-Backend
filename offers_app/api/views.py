from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .serializers import OfferCreateSerializer, OfferSerializer, DetailSerializer
from .permissions import IsBusinessUser, IsOfferOwner
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
            return OfferSerializer
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


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]

    def patch(self, request, *args, **kwargs):
        offer = self.get_object()
        err = self._update_details(offer, (request.data or {}).get('details'))
        
        if err:
            return err
        
        self._update_scalar_fields(offer, request.data or {})
        details_qs = self._recalc_and_save(offer)

        return Response(self._build_response(offer, details_qs), status=status.HTTP_200_OK)

    def _update_scalar_fields(self, offer, data):
        for field in ['title', 'description']:
            if field in data:
                setattr(offer, field, data.get(field))
    
    def _update_details(self, offer, details_payload):
        if details_payload is None:
            return None
        if isinstance(details_payload, list):
            existing_by_type = {d.offer_type: d for d in offer.details.all()}
        for item in details_payload:
            if isinstance(item, dict):
                offer_type = item.get('offer_type')
            if offer_type not in existing_by_type:
                return Response({'offer_type': f'Unknown offer_type: {offer_type}'}, status=status.HTTP_400_BAD_REQUEST)
            detail = existing_by_type[offer_type]
            for f in ['title', 'revisions', 'delivery_time_in_days', 'price', 'features']:
                if f in item:
                    setattr(detail, f, item.get(f))
            detail.save()
        return None

    def _recalc_and_save(self, offer):
        details_qs = offer.details.all()
        if details_qs.exists():
            offer.min_price = min(d.price for d in details_qs)
            offer.min_delivery_time = min(d.delivery_time_in_days for d in details_qs)
        offer.updated_at = timezone.now()
        offer.save(update_fields=['title', 'description', 'min_price', 'min_delivery_time', 'updated_at'])
        return details_qs

    def _build_response(self, offer, details_qs):
        try:
            image_url = offer.image.url
        except Exception:
            image_url = None
        return {
            'id': offer.id,
            'title': offer.title,
            'image': image_url,
            'description': offer.description,
            'details': DetailSerializer(details_qs, many=True).data,
        }

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
