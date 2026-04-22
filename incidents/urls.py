from django.urls import path

from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.incidents_list, name='list'),
    path('new/', views.incident_create, name='create'),
    path('<int:pk>/', views.incident_detail, name='detail'),
]
