from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'offer_type', 'status']
    list_filter = ['offer_type', 'status']

admin.site.register(Order, OrderAdmin)
