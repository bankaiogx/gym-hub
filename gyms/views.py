from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GymForm, ReviewForm
from .models import Gym


def home(request):
    return render(request, 'gyms/home.html')


def gym_list(request):
    gyms = Gym.objects.annotate(average_rating=Avg('reviews__rating'))
    return render(request, 'gyms/gym_list.html', {'gyms': gyms})


def gym_detail(request, slug):
    gym = get_object_or_404(Gym, slug=slug)
    reviews = gym.reviews.select_related('user')
    average_rating = gym.reviews.aggregate(Avg('rating'))['rating__avg']
    user_review = None
    review_form = None

    if request.user.is_authenticated:
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
            'review_form': review_form,
            'user_review': user_review,
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

    return render(request, 'gyms/add_gym.html', {'form': form})


@login_required
def add_review(request, slug):
    gym = get_object_or_404(Gym, slug=slug)

    if request.method != 'POST':
        return redirect('gym_detail', slug=gym.slug)

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
            'review_form': form,
            'user_review': None,
        },
    )
