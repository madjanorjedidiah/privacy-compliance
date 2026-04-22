from django.urls import path

from . import views

app_name = 'ops'

urlpatterns = [
    path('health/', views.health, name='health'),
    path('readyz/', views.readyz, name='readyz'),
]
