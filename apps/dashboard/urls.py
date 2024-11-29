from django.urls import path
from . import views
from .views import upload_csv, OrderListView

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('upload/', upload_csv, name='upload_csv'),
    path('orders/', OrderListView.as_view(), name='order_list'),
]