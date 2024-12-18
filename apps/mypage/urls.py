from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('edit/', views.edit_profile_view, name='edit'),
]