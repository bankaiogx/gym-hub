from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            authentication_form=LoginForm,
            template_name='gyms/login.html',
        ),
        name='login',
    ),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('account/submitted-gyms/', views.my_submitted_gyms, name='my_submitted_gyms'),
    path('gyms/', views.gym_list, name='gym_list'),
    path('gyms/add/', views.add_gym, name='add_gym'),
    path('gyms/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('gyms/<slug:slug>/reviews/add/', views.add_review, name='add_review'),
    path('gyms/<slug:slug>/', views.gym_detail, name='gym_detail'),
]
