from django.urls import path
from . import views

app_name = 'yms_edit'

urlpatterns = [
    path('', views.edit_view, name='edit_view'),
]