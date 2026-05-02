from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.db.models import Avg, BooleanField, Count, Exists, OuterRef, Q, Value
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import GymForm, ReviewForm
from .models import Amenity, Favourite, Gym


def home(request):
    return render(request, 'gyms/home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('gym_list')
    else:
        form = UserCreationForm()

    return render(request, 'gyms/signup.html', {'form': form})


def gym_list(request):
    query = request.GET.get('q', '').strip()
    price = request.GET.get('price', '').strip()
    min_rating = request.GET.get('rating', '').strip()
    sort = request.GET.get('sort', 'az').strip()
    bookmarked_only = request.GET.get('bookmarked') == '1'
    selected_amenity_ids = request.GET.getlist('amenities')
    sort_choices = [
        ('newest', 'Newest'),
        ('highest_rated', 'Highest rated'),
        ('most_bookmarked', 'Most bookmarked'),
        ('az', 'A-Z'),
    ]
    valid_sort_values = {value for value, label in sort_choices}
    if sort not in valid_sort_values:
        sort = 'az'

    gyms = Gym.objects.prefetch_related('amenities').annotate(
        average_rating=Avg('reviews__rating'),
        bookmark_count=Count('favourites', distinct=True),
    )

    if request.user.is_authenticated:
        gyms = gyms.annotate(
            is_bookmarked=Exists(
                Favourite.objects.filter(gym=OuterRef('pk'), user=request.user)
            )
        )
    else:
        gyms = gyms.annotate(
            is_bookmarked=Value(False, output_field=BooleanField())
        )

    if query:
        gyms = gyms.filter(
            Q(name__icontains=query)
            | Q(city__icontains=query)
            | Q(postcode__icontains=query)
            | Q(address__icontains=query)
            | Q(description__icontains=query)
        )

    if price:
        gyms = gyms.filter(price_range=price)

    if selected_amenity_ids:
        gyms = gyms.filter(amenities__id__in=selected_amenity_ids).distinct()

    if min_rating:
        gyms = gyms.filter(average_rating__gte=min_rating)

    if bookmarked_only:
        if request.user.is_authenticated:
            gyms = gyms.filter(favourites__user=request.user)
        else:
            gyms = gyms.none()

    if sort == 'newest':
        gyms = gyms.order_by('-created_at', 'name')
    elif sort == 'highest_rated':
        gyms = gyms.order_by('-average_rating', 'name')
    elif sort == 'most_bookmarked':
        gyms = gyms.order_by('-bookmark_count', 'name')
    else:
        gyms = gyms.order_by('name')

    return render(
        request,
        'gyms/gym_list.html',
        {
            'gyms': gyms,
            'query': query,
            'price': price,
            'min_rating': min_rating,
            'sort': sort,
            'bookmarked_only': bookmarked_only,
            'amenities': Amenity.objects.all(),
            'selected_amenity_ids': selected_amenity_ids,
            'active_filter_count': (
                len(selected_amenity_ids)
                + (1 if price else 0)
                + (1 if min_rating else 0)
                + (1 if bookmarked_only else 0)
            ),
            'price_choices': Gym.PRICE_CHOICES,
            'rating_choices': [5, 4, 3, 2, 1],
            'sort_choices': sort_choices,
        },
    )


def gym_detail(request, slug):
    gym = get_object_or_404(Gym.objects.prefetch_related('amenities'), slug=slug)
    reviews = gym.reviews.select_related('user')
    average_rating = gym.reviews.aggregate(Avg('rating'))['rating__avg']
    bookmark_count = gym.favourites.count()
    is_bookmarked = False
    user_review = None
    review_form = None

    if request.user.is_authenticated:
        is_bookmarked = gym.favourites.filter(user=request.user).exists()
        user_review = reviews.filter(user=request.user).first()
        if user_review is None:
            review_form = ReviewForm()

    return render(
        request,
        'gyms/gym_detail.html',
        {
            'gym': gym,
            'reviews': reviews,
            'average_rating': average_rating,
            'bookmark_count': bookmark_count,
            'is_bookmarked': is_bookmarked,
            'review_form': review_form,
            'user_review': user_review,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        },
    )


@login_required
def add_gym(request):
    if request.method == 'POST':
        form = GymForm(request.POST, request.FILES)
        if form.is_valid():
            gym = form.save(commit=False)
            gym.owner = request.user
            gym.save()
            form.save_m2m()
            return redirect('gym_detail', slug=gym.slug)
    else:
        form = GymForm()

    return render(
        request,
        'gyms/add_gym.html',
        {
            'form': form,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        },
    )


@login_required
@require_POST
def add_review(request, slug):
    gym = get_object_or_404(Gym, slug=slug)

    if gym.reviews.filter(user=request.user).exists():
        return redirect('gym_detail', slug=gym.slug)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.gym = gym
        review.user = request.user
        review.save()
        return redirect('gym_detail', slug=gym.slug)

    reviews = gym.reviews.select_related('user')
    average_rating = gym.reviews.aggregate(Avg('rating'))['rating__avg']
    return render(
        request,
        'gyms/gym_detail.html',
        {
            'gym': gym,
            'reviews': reviews,
            'average_rating': average_rating,
            'bookmark_count': gym.favourites.count(),
            'is_bookmarked': gym.favourites.filter(user=request.user).exists(),
            'review_form': form,
            'user_review': None,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        },
    )


@login_required
@require_POST
def toggle_bookmark(request, slug):
    gym = get_object_or_404(Gym, slug=slug)
    bookmark, created = Favourite.objects.get_or_create(
        gym=gym,
        user=request.user,
    )

    if not created:
        bookmark.delete()

    redirect_to = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if url_has_allowed_host_and_scheme(
        redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(redirect_to)

    return redirect('gym_detail', slug=gym.slug)
