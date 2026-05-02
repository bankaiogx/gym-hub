from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Avg, BooleanField, Count, Exists, OuterRef, Q, Value
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import GymForm, ReviewForm
from .models import Favourite, Gym


def home(request):
    return render(request, 'gyms/home.html')


def gym_list(request):
    query = request.GET.get('q', '').strip()
    price = request.GET.get('price', '').strip()
    gyms = Gym.objects.annotate(
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
            | Q(description__icontains=query)
        )

    if price:
        gyms = gyms.filter(price_range=price)

    return render(
        request,
        'gyms/gym_list.html',
        {
            'gyms': gyms,
            'query': query,
            'price': price,
            'price_choices': Gym.PRICE_CHOICES,
        },
    )


def gym_detail(request, slug):
    gym = get_object_or_404(Gym, slug=slug)
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
        form = GymForm(request.POST)
        if form.is_valid():
            gym = form.save(commit=False)
            gym.owner = request.user
            gym.save()
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
