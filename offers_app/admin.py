from django.contrib import admin
from .models import Offer, Detail


class DetailInline(admin.TabularInline):
    model = Detail
    extra = 0
    fields = ['offer_type', 'title', 'price', 'delivery_time_in_days', 'revisions', 'features']


class OfferAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'updated_at', 'min_price']
    list_filter = ['user']
    inlines = [DetailInline]


admin.site.register(Offer, OfferAdmin)
