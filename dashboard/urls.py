from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('gap-map/', views.gap_map_view, name='gap_map'),
]
