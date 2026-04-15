from django.contrib import admin
from .models import Amenity, Gym, Review, Favourite, GymAmenity


admin.site.register(Amenity)
admin.site.register(Gym)
admin.site.register(Review)
admin.site.register(Favourite)
admin.site.register(GymAmenity)