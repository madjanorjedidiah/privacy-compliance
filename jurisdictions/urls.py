from django.urls import path

from . import views

app_name = 'jurisdictions'

urlpatterns = [
    path('', views.jurisdictions_list, name='list'),
    path('framework/<str:code>/', views.framework_detail, name='framework'),
    path('requirement/<int:pk>/', views.requirement_detail, name='requirement'),
]
