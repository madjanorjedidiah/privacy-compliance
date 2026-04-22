from django.urls import path

from . import views

app_name = 'public'

urlpatterns = [
    path('privacy/', views.privacy_notice, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('cookies/', views.cookies, name='cookies'),
]
