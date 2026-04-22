from django.urls import path

from . import views

app_name = 'dpia'

urlpatterns = [
    path('', views.dpia_list, name='list'),
    path('new/', views.dpia_create, name='create'),
    path('<int:pk>/', views.dpia_detail, name='detail'),
    path('<int:pk>/edit/', views.dpia_edit, name='edit'),
]
