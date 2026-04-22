from django.urls import path

from . import views

app_name = 'training'

urlpatterns = [
    path('', views.module_list, name='list'),
    path('modules/new/', views.module_create, name='module_create'),
    path('records/new/', views.record_create, name='record_create'),
]
