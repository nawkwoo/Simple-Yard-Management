from django.urls import path
from . import views
from .views import TransactionListView

app_name = 'yms_view'

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='view_page'),
]