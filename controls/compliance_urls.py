from django.urls import path

from . import compliance_views as views

app_name = 'compliance'

urlpatterns = [
    path('', views.compliance_home, name='home'),
    path('jurisdiction/<str:code>/', views.compliance_jurisdiction, name='jurisdiction'),
    path('control/<int:control_id>/advance/', views.compliance_advance, name='advance'),
]
