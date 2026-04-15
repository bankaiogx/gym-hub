from django.shortcuts import render, get_object_or_404
from .models import Gym


def home(request):
    return render(request, 'gyms/home.html')


def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'gyms/gym_list.html', {'gyms': gyms})


def gym_detail(request, slug):
    gym = get_object_or_404(Gym, slug=slug)
    return render(request, 'gyms/gym_detail.html', {'gym': gym})