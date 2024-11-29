from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    path('', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit'),
]