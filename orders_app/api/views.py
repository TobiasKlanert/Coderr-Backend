"""
orders_app.api.views
---------------------

Module summary
This module provides API views for creating, listing and managing `Order`
instances. It exposes endpoints to:

- List/create orders for the authenticated user (`OrderListCreateView`).
- Retrieve, partially update (business side) or delete an order
    (`OrderDetailView`).
- Query counts for a business: active orders and completed orders
    (`OrderCountView`, `OrderCompleteView`).

Behavior & permissions
- Customers may create orders. Business users may update order status.
- Deletions are restricted to admin users.
- Views use serializer classes `OrderCreateSerializer` (for creation with
    validation) and `OrderSerializer` (for read responses).
"""

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
    """List orders for the authenticated user or create a new order.

    GET (list):
      - Requires authentication.
      - If the authenticated user is a customer (user.type == 'customer'),
        returns orders where `customer_user == user`.
      - Otherwise returns orders where `business_user == user`.
      - Results are ordered by `-created_at`.

    POST (create):
      - Requires an authenticated customer (IsAuthenticated + IsCustomerUser).
      - Uses `OrderCreateSerializer` and expects validated payload including
        an `offer_detail_id` that must exist in `offers_app.models.Detail`.
      - On success returns 201 with the created order serialized by
        `OrderSerializer`.
    """

    queryset = Order.objects.all()

    def get_permissions(self):
        """Return permission instances depending on HTTP method.

        - POST: IsAuthenticated + IsCustomerUser
        - GET: IsAuthenticated
        """

        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Select serializer class based on HTTP method.

        - POST uses `OrderCreateSerializer` to validate creation input.
        - GET uses `OrderSerializer` for read-only representations.
        """

        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """Return a queryset scoped to the authenticated user.

        - Unauthenticated requests receive an empty queryset.
        - Customers see orders they created; businesses see orders for them.
        """

        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if getattr(user, 'type', None) == 'customer':
            return Order.objects.filter(customer_user=user).order_by('-created_at')
        return Order.objects.filter(business_user=user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Create a new Order.

        This view delegates validation to `OrderCreateSerializer`. After
        validating, it ensures the referenced `offer_detail_id` exists and
        then saves the order associated with the request user.

        Returns 201 with the serialized order on success.
        """

        serializer = OrderCreateSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        offer_detail_id = serializer.validated_data.get('offer_detail_id')
        get_object_or_404(Detail, id=offer_detail_id)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    """Retrieve, partially update or delete a single Order.

    GET: requires authentication and returns the serialized Order.

    PATCH: used by the business owner to update the order status. The caller
    must be the `business_user` assigned to the order. Expected payload: {"status": "<new_status>"}.

    DELETE: restricted to admin users.
    """

    def get_permissions(self):
        """Return permission instances depending on HTTP method.

        - DELETE: IsAdminUser
        - GET/PATCH: IsAuthenticated (additional owner check enforced in PATCH)
        """

        if self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def delete(self, request, *args, **kwargs):
        """Delete an Order (admin only)."""

        return self.destroy(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """Partially update an Order's status.

        Only the `business_user` associated with the order may change its status.
        The view validates the presence of `status` in the payload and that
        the provided value is one of the allowed `Order.Status` choices.
        """

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
    """Return the count of in-progress orders for a business user.

    Path parameter: `pk` is the id of the business user. The view validates
    that the user exists and has type `BUSINESS`, then returns a JSON object
    {"order_count": <int>} with the number of orders in 'in_progress' state.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(User, id=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=pk,
            status='in_progress'
        ).count()
        return Response({"order_count": count})


class OrderCompleteView(APIView):
    """Return the count of completed orders for a business user.

    Path parameter: `pk` is the id of the business user. Returns
    {"completed_order_count": <int>}.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        get_object_or_404(User, id=pk, type=User.Type.BUSINESS)
        count = Order.objects.filter(
            business_user=pk,
            status='completed'
        ).count()
        return Response({"completed_order_count": count})
