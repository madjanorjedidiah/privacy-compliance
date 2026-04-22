from django.urls import path

from . import data_subject_views, views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('me/export/', data_subject_views.export_my_data, name='export_me'),
    path('me/delete/', data_subject_views.delete_my_account, name='delete_me'),
]
