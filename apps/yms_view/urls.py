# apps/yms_view/urls.py

from django.urls import path
from .views import (
    TransactionListView,
    YardListView,
    MoveEquipmentView,
)

app_name = 'yms_view'

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/yard/', YardListView.as_view(), name='yard_ids'),
    path('transactions/move/', MoveEquipmentView.as_view(), name='move-equipment'),
]
