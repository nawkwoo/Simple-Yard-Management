from django.urls import path
from . import views

app_name = 'yms'

urlpatterns = [
    path('', views.yms, name='yms'),
]
