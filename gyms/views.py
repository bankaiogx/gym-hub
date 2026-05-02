from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.conf import settings
from django.db.models import Avg, BooleanField, Count, Exists, OuterRef, Q, Value
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from .forms import GymForm, ReviewForm, SignupForm
from .models import Amenity, Favourite, Gym, Review


def home(request):
    return render(request, 'gyms/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('gym_list')
    else:
        form = SignupForm()

    return render(request, 'gyms/signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    logout(request)
    return redirect('gym_list')


@login_required
def account_dashboard(request):
    return render(
        request,
        'gyms/account.html',
        {
            'submitted_count': request.user.gyms.count(),
            'bookmark_count': request.user.favourites.count(),
            'review_count': request.user.reviews.count(),
        },
    )


def gym_card_queryset(request):
    gyms = Gym.objects.prefetch_related('amenities').annotate(
        average_rating=Avg('reviews__rating'),
        bookmark_count=Count('favourites', distinct=True),
    )

    if request.user.is_authenticated:
        return gyms.annotate(
            is_bookmarked=Exists(
                Favourite.objects.filter(gym=OuterRef('pk'), user=request.user)
            )
        )

    return gyms.annotate(
        is_bookmarked=Value(False, output_field=BooleanField())
    )


@login_required
def my_bookmarks(request):
    gyms = gym_card_queryset(request).filter(favourites__user=request.user)
    return render(request, 'gyms/my_bookmarks.html', {'gyms': gyms})


@login_required
def my_submitted_gyms(request):
    gyms = gym_card_queryset(request).filter(owner=request.user)
    return render(request, 'gyms/my_submitted_gyms.html', {'gyms': gyms})


def gym_list(request):
    query = request.GET.get('q', '').strip()
    price = request.GET.get('price', '').strip()
    min_rating = request.GET.get('rating', '').strip()
    sort = request.GET.get('sort', 'az').strip()
    bookmarked_only = request.GET.get('bookmarked') == '1'
    submitted_only = request.GET.get('submitted') == '1'
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

    gyms = gym_card_queryset(request)

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

    if submitted_only:
        if request.user.is_authenticated:
            gyms = gyms.filter(owner=request.user)
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
            'submitted_only': submitted_only,
            'amenities': Amenity.objects.all(),
            'selected_amenity_ids': selected_amenity_ids,
            'active_filter_count': (
                len(selected_amenity_ids)
                + (1 if price else 0)
                + (1 if min_rating else 0)
                + (1 if bookmarked_only else 0)
                + (1 if submitted_only else 0)
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
def edit_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return HttpResponseForbidden('You can only edit your own reviews.')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('gym_detail', slug=review.gym.slug)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        'gyms/edit_review.html',
        {
            'form': form,
            'review': review,
            'gym': review.gym,
        },
    )


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return HttpResponseForbidden('You can only delete your own reviews.')

    gym_slug = review.gym.slug
    review.delete()
    return redirect('gym_detail', slug=gym_slug)


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
