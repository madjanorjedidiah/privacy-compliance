from django.urls import path

from . import views

app_name = 'risks'

urlpatterns = [
    path('', views.risks_list, name='list'),
    path('new/', views.risk_create, name='create'),
    path('<int:pk>/edit/', views.risk_edit, name='edit'),
]
