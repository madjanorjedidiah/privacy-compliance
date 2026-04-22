from django.urls import path

from . import views

app_name = 'controls'

urlpatterns = [
    path('', views.controls_list, name='list'),
    path('<int:pk>/', views.control_detail, name='detail'),
    path('<int:pk>/quick-status/', views.control_quick_status, name='quick_status'),
]
