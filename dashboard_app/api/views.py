from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from auth_app.models import User
from offers_app.models import Offer
from orders_app.models import Order
from reviews_app.models import Review

class DashboardOverviewView(APIView):
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
