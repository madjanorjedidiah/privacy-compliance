from django.urls import path

from . import views

app_name = 'dsar'

urlpatterns = [
    path('', views.dsar_list, name='list'),
    path('new/', views.dsar_create, name='create'),
    path('<int:pk>/', views.dsar_detail, name='detail'),
]
