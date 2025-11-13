from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from auth_app.models import User
from offers_app.models import Offer
from orders_app.models import Order
from reviews_app.models import Review

class DashboardOverviewView(APIView):
    """
    API view that returns a small dashboard overview consisting of basic counts and an aggregated review score.
    Provides:
    - review_count (int): total number of Review records.
    - average_rating (float): average of Review.rating rounded to 1 decimal place; returns 0.0 if there are no reviews.
    - business_profile_count (int): number of User records with type='business'.
    - offer_count (int): total number of Offer records.
    Behavior:
    - HTTP method: GET
    - Authentication/Permissions: AllowAny (no authentication required).
    - Performs a DB aggregation for the average rating and simple counts for the other metrics.
    - Returns a rest_framework.response.Response with a JSON object containing the fields above and HTTP 200 on success.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        avg_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        data = {
            "review_count": Review.objects.count(),
            "average_rating": round(avg_rating, 1) if avg_rating is not None else 0.0,
            "business_profile_count": User.objects.filter(type='business').count(),
            "offer_count": Offer.objects.count()
        }
        return Response(data)
