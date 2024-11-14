from django.urls import path
from . import views

app_name = 'yms_view'

urlpatterns = [
    path('', views.view_page, name='view_page'),
]