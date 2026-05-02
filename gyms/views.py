from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GymForm
from .models import Gym


def home(request):
    return render(request, 'gyms/home.html')


def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'gyms/gym_list.html', {'gyms': gyms})


def gym_detail(request, slug):
    gym = get_object_or_404(Gym, slug=slug)
    return render(request, 'gyms/gym_detail.html', {'gym': gym})


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
