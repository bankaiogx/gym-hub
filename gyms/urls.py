from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('gyms/', views.gym_list, name='gym_list'),
    path('gyms/add/', views.add_gym, name='add_gym'),
    path('gyms/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('gyms/<slug:slug>/reviews/add/', views.add_review, name='add_review'),
    path('gyms/<slug:slug>/', views.gym_detail, name='gym_detail'),
]
