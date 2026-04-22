from django.urls import path

from . import views

app_name = 'retention'

urlpatterns = [
    path('', views.policy_list, name='list'),
    path('new/', views.policy_create, name='create'),
    path('<int:pk>/edit/', views.policy_edit, name='edit'),
]
