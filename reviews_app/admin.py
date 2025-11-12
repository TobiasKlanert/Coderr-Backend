from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['business_user__username', 'reviewer__username', 'rating', 'created_at']
    list_filter = ['rating']

admin.site.register(Review, ReviewAdmin)