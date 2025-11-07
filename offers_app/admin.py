from django.contrib import admin
from .models import Offer, Detail


class DetailInline(admin.TabularInline):
    model = Detail
    extra = 0
    fields = ['offer_type', 'title', 'price', 'delivery_time_in_days', 'revisions', 'features']


class OfferAdmin(admin.ModelAdmin):
    list_display = ['user_username', 'title', 'created_at', 'updated_at', 'min_price']
    list_filter = []

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'user'
    user_username.admin_order_field = 'user__username'
    inlines = [DetailInline]


class UserUsernameFilter(admin.SimpleListFilter):
    title = 'user'
    parameter_name = 'user_username'

    def lookups(self, request, model_admin):
        usernames = (model_admin.model.objects
                     .values_list('user__username', flat=True)
                     .distinct())
        return [(u, u) for u in usernames if u]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(user__username=value)
        return queryset

OfferAdmin.list_filter = [UserUsernameFilter]


admin.site.register(Offer, OfferAdmin)
