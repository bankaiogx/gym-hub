from django.contrib import admin
from django.utils import timezone

from .models import Amenity, Gym, Review, Favourite, GymAmenity


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    # Keep amenities easy to find and manage in admin.
    list_display = ('name', 'icon', 'created_at')
    search_fields = ('name',)


class GymAmenityInline(admin.TabularInline):
    # Allows amenities to be attached while editing a gym.
    model = GymAmenity
    extra = 1


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    # Show moderation fields clearly in the gym admin list.
    list_display = ('name', 'city', 'price_range', 'status', 'approved_by', 'approved_at', 'created_at')
    list_filter = ('status', 'city', 'price_range', 'amenities')
    search_fields = ('name', 'city', 'postcode')
    inlines = (GymAmenityInline,)
    actions = ('approve_selected_gyms', 'reject_selected_gyms')

    @admin.action(description='Approve selected gyms')
    def approve_selected_gyms(self, request, queryset):
        # Approved gyms become visible on the public gym list.
        queryset.update(
            status=Gym.STATUS_APPROVED,
            approved_at=timezone.now(),
            approved_by=request.user,
        )

    @admin.action(description='Reject selected gyms')
    def reject_selected_gyms(self, request, queryset):
        # Rejected gyms stay hidden from normal public views.
        queryset.update(
            status=Gym.STATUS_REJECTED,
            approved_at=None,
            approved_by=None,
        )


admin.site.register(Review)
admin.site.register(Favourite)
admin.site.register(GymAmenity)
