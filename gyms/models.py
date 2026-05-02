from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Gym(models.Model):
    PRICE_CHOICES = [
        ('budget', 'Budget'),
        ('mid', 'Mid-range'),
        ('premium', 'Premium'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='gyms'
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    google_place_id = models.CharField(max_length=255, blank=True)
    google_rating = models.FloatField(null=True, blank=True)
    opening_hours_text = models.TextField(blank=True)
    image = models.FileField(upload_to='gym_images/', blank=True)
    image_url = models.URLField(max_length=1000, blank=True)
    website = models.URLField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    price_range = models.CharField(
        max_length=20,
        choices=PRICE_CHOICES,
        default='mid'
    )
    opening_hours = models.CharField(max_length=255, blank=True)
    amenities = models.ManyToManyField(
        'Amenity',
        through='GymAmenity',
        related_name='gyms',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name', 'address'],
                name='unique_gym_per_owner_name_address'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.city}")
            slug = base_slug
            counter = 1
            while Gym.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('gym', 'user')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='review_rating_between_1_and_5'
            ),
        ]

    def __str__(self):
        return f"{self.gym.name} review by {self.user.username}"


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'gym'],
                name='unique_favourite_per_user_per_gym'
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.gym.name}"


class GymAmenity(models.Model):
    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['gym__name', 'amenity__name']
        constraints = [
            models.UniqueConstraint(
                fields=['gym', 'amenity'],
                name='unique_amenity_per_gym'
            )
        ]

    def __str__(self):
        return f"{self.gym.name} - {self.amenity.name}"
