from django.shortcuts import get_object_or_404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsCustomerUser
from ..models import Order
from offers_app.models import Detail
from auth_app.models import User


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
        serializer = OrderCreateSerializer(
            data=request.data, context={'request': request})
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

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user

        if not user.is_authenticated or order.business_user_id != user.id:
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)

        new_status = (request.data or {}).get('status')
        if new_status is None:
            return Response({'status': 'This field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = {choice for (choice, _label) in Order.Status.choices}
        if new_status not in valid_statuses:
            return Response({'status': f'Invalid value. Allowed: {sorted(valid_statuses)}'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(User, id=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=pk,
            status='in_progress'
        ).count()
        return Response({"order_count": count})


class OrderCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(User, id=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=pk,
            status='completed'
        ).count()
        return Response({"completed_order_count": count})
