from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Amenity(models.Model):
    # Amenities are chosen by users/admins instead of pulled from Google.
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class Gym(models.Model):
    # Moderation status controls whether a submitted gym appears publicly.
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

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
    image = models.ImageField(upload_to='gym_images/', blank=True, null=True)
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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_gyms'
    )

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
            # Use name and city to create readable detail-page URLs.
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
    # Ratings are limited to a simple 1-5 star scale.
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
        constraints = [
            # A user can only review the same gym once.
            models.UniqueConstraint(
                fields=['gym', 'user'],
                name='unique_review_per_user_per_gym'
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='review_rating_between_1_and_5'
            ),
        ]

    def __str__(self):
        return f"{self.gym.name} review by {self.user.username}"


class Favourite(models.Model):
    # Bookmarks connect a user to a gym they want to save.
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
            # Prevent duplicate bookmarks for the same user and gym.
            models.UniqueConstraint(
                fields=['user', 'gym'],
                name='unique_favourite_per_user_per_gym'
            )
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.gym.name}"


class GymAmenity(models.Model):
    # Through model keeps gym and amenity links unique.
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
