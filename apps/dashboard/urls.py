# apps/dashboard/urls.py

from django.urls import path
from .views import OrderListView, upload_csv, home  # home 뷰 추가

app_name = 'dashboard'

urlpatterns = [
    path('', home, name='home'),
    path('upload-orders/', upload_csv, name='upload_csv'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    # 다른 URL 패턴들...
]
