from django.urls import path

from . import views

app_name = 'templates'

urlpatterns = [
    path('', views.templates_list, name='list'),
    path('<int:pk>/preview/', views.template_preview, name='preview'),
    path('<int:pk>/generate/', views.template_generate, name='generate'),
    path('documents/<int:pk>/', views.document_detail, name='document'),
    path('documents/<int:pk>/download/', views.document_download, name='download'),
]
