from django.contrib import admin
from .models import Amenity, Gym, Review, Favourite, GymAmenity


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'created_at')
    search_fields = ('name',)


class GymAmenityInline(admin.TabularInline):
    model = GymAmenity
    extra = 1


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price_range', 'created_at')
    list_filter = ('price_range', 'amenities')
    search_fields = ('name', 'city', 'address')
    inlines = (GymAmenityInline,)


admin.site.register(Review)
admin.site.register(Favourite)
admin.site.register(GymAmenity)
