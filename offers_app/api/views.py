"""
offers_app.api.views
----------------------

Module summary
This module exposes the REST API views for the `offers_app` and documents
their behaviors, permissions and expected inputs/outputs. The main views are:

- `OfferListCreateView` - list offers (public) and create new offers (business users).
- `DetailRetrieveView` - retrieve a single detail row for an offer.
- `OfferDetailView` - retrieve, update or delete a specific offer (owner-only for writes).
"""

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .serializers import OfferCreateSerializer, OfferSerializer, DetailSerializer
from .permissions import IsBusinessUser, IsOfferOwner
from ..models import Offer, Detail


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination class tuned for offers listing endpoints.

    - Default page size: 6
    - Client may request a custom `page_size` up to `max_page_size` (12)
    """

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 12


class OfferListCreateView(generics.ListCreateAPIView):
    """List and create Offers.

    GET (list):
      - Public endpoint (AllowAny) returning a paginated list of offers.
      - Supports filtering (`user__id`, `min_price`), searching (title/description)
        and ordering (by `updated_at`, `min_price`).
      - Optional query parameter `max_delivery_time` (integer) filters offers
        with `min_delivery_time <= max_delivery_time`.

    POST (create):
      - Requires authenticated business users (IsAuthenticated + IsBusinessUser).
      - Uses `OfferCreateSerializer` which expects nested `details` (three items:
        basic, standard, premium) and associates the created offer with the
        authenticated user from `request`.
    """

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user__id']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        """Return the appropriate serializer for the request method.

        - GET: `OfferSerializer` (read-only compact representation)
        - POST: `OfferCreateSerializer` (nested create behavior)
        """

        if self.request.method == 'GET':
            return OfferSerializer
        return OfferCreateSerializer

    def get_permissions(self):
        """Return permission instances depending on HTTP method.

        - GET: AllowAny (public listing)
        - POST: IsAuthenticated + IsBusinessUser (only business accounts may create)
        """

        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAuthenticated(), IsBusinessUser()]

    def get_queryset(self):
        """ 
        Return a queryset of Offer objects optionally filtered by request query parameters.

        This method builds the base queryset for list views and applies two optional
        filters based on query parameters provided in self.request.query_params:

        Parameters accepted via query string:
        - max_delivery_time: If supplied and non-empty, must be an integer. The
            returned queryset will include offers whose `min_delivery_time` is less than
            or equal to this value.
        - min_price: If supplied and non-empty, must be an integer. The returned
            queryset will include offers whose `min_price` is greater than or equal to
            this value.

        Returns:
        - django.db.models.QuerySet: the filtered queryset of Offer objects. 
        """

        queryset = Offer.objects.all()

        time_param = self.request.query_params.get('max_delivery_time', None)
        if time_param is not None and str(time_param).strip() != '':
            try:
                max_days = int(time_param)
            except (TypeError, ValueError):
                raise ValidationError(
                    {'max_delivery_time': 'Expected an integer value.'}
                )
            queryset = queryset.filter(min_delivery_time__lte=max_days)

        price_param = self.request.query_params.get('min_price', None)
        if price_param is not None and str(price_param).strip() != '':
            try:
                min_price_filter = int(price_param)
            except (TypeError, ValueError):
                raise ValidationError(
                    {'min_price': 'Expected an integer value.'}
                )
            queryset = queryset.filter(min_price__gte=min_price_filter)

        return queryset


class DetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single Offer Detail by id.

    - Method: GET
    - Permissions: default DRF permission classes (in this project it is allowed
        wherever the view is used; view-level permission wrappers may apply).
    - Response: serialized Detail object.
    """

    queryset = Detail.objects.all()
    serializer_class = DetailSerializer


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific Offer instance.

    GET:
      - Requires authentication (IsAuthenticated).
      - Returns the OfferSerializer representation.

    PATCH:
      - Requires the requester to be the owner (IsAuthenticated + IsOfferOwner).
      - Handles partial updates for scalar fields (`title`, `description`) and
        accepts an optional `details` payload to modify existing Detail rows.
      - The `details` payload is expected to be a list of dicts, each identifying
        a detail by `offer_type` and containing fields to update for that detail.
      - After detail/scalar updates, cached summary fields (`min_price`,
        `min_delivery_time`) are recalculated and persisted.

    DELETE:
      - Requires owner permissions and deletes the offer.
    """

    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    def get_permissions(self):
        """Return permissions depending on HTTP method.

        - GET: IsAuthenticated
        - PATCH/PUT/DELETE: IsAuthenticated + IsOfferOwner (only owners may modify)
        """

        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]

    def patch(self, request, *args, **kwargs):
        """Handle partial updates for an Offer including nested detail updates.

        Workflow:
        1. Load the Offer instance.
        2. Try to apply detail updates using `_update_details`. If that returns
           a `Response` object (error), return it immediately.
        3. Update scalar fields via `_update_scalar_fields`.
        4. Recalculate cached summary fields and persist changes via
           `_recalc_and_save`.
        5. Return a 200 response with a compact build of the offer data.

        Returns:
          - 200 with updated offer payload on success
          - 400 with error detail if invalid `offer_type` or payload
        """

        offer = self.get_object()
        err = self._update_details(offer, (request.data or {}).get('details'))

        if err:
            return err

        self._update_scalar_fields(offer, request.data or {})
        details_qs = self._recalc_and_save(offer)

        return Response(self._build_response(offer, details_qs), status=status.HTTP_200_OK)

    def _update_scalar_fields(self, offer, data):
        """Update simple scalar fields on the Offer instance.

        Only `title` and `description` are considered here. The method mutates
        the `offer` instance in memory; persistence happens in `_recalc_and_save`.
        """

        for field in ['title', 'description']:
            if field in data:
                setattr(offer, field, data.get(field))

    def _update_details(self, offer, details_payload):
        """Apply updates to existing Detail rows for an Offer.

        Expected `details_payload`:
          - None: no detail changes (returns None)
          - list of dicts: each dict should include `offer_type` to identify
            the Detail and any subset of updatable Detail fields
            (title, revisions, delivery_time_in_days, price, features).

        Behavior:
          - Builds a mapping of existing details by `offer_type`.
          - For each item, finds the matching Detail and updates the fields
            present in the item, then saves the Detail instance.
          - If an unknown `offer_type` is provided, returns a DRF `Response`
            with status 400 explaining the unknown type.

        Returns:
          - None on success
          - `Response` instance on validation error (caller should return it)
        """

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
        """Recalculate cached summary fields and persist the Offer.

        - Recomputes `min_price` and `min_delivery_time` from related Detail rows
          if they exist.
        - Sets `updated_at` to now and saves changed fields.
        - Returns the details queryset used for response construction.
        """

        details_qs = offer.details.all()
        if details_qs.exists():
            offer.min_price = min(d.price for d in details_qs)
            offer.min_delivery_time = min(
                d.delivery_time_in_days for d in details_qs)
        offer.updated_at = timezone.now()
        offer.save(update_fields=['title', 'description',
                   'min_price', 'min_delivery_time', 'updated_at'])
        return details_qs

    def _build_response(self, offer, details_qs):
        """Construct a compact response payload for the updated Offer.

        Returns a simple dict with id, title, image URL (or None), description
        and serialized details.
        """

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
        """Delete the Offer instance (owner only).

        Delegates to the generic `destroy` implementation provided by DRF.
        """

        return self.destroy(request, *args, **kwargs)
