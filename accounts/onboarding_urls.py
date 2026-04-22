from django.urls import path

from . import onboarding_views as views

app_name = 'onboarding'

urlpatterns = [
    path('', views.basics, name='basics'),
    path('profile/', views.profile, name='profile'),
    path('review/', views.review, name='review'),
]
