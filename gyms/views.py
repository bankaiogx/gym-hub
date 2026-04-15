from django.shortcuts import render
from .models import Gym


def home(request):
    return render(request, 'gyms/home.html')


def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'gyms/gym_list.html', {'gyms': gyms})