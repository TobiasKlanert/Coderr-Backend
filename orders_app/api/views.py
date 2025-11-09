from django.shortcuts import get_object_or_404

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsCustomerUser
from ..models import Order
from offers_app.models import Detail


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if getattr(user, 'type', None) == 'customer':
            return Order.objects.filter(customer_user=user).order_by('-created_at')
        return Order.objects.filter(business_user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        offer_detail_id = serializer.validated_data.get('offer_detail_id')
        get_object_or_404(Detail, id=offer_detail_id)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)