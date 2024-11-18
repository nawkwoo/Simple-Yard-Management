from django.urls import path
from . import views

app_name = 'yms_edit'

# urlpatterns = [
#     path('equipment/', views.EquipmentListView.as_view(), name='equipment-list'),
#     path('equipment/add/', views.EquipmentCreateView.as_view(), name='equipment-add'),
#     path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
# ]

urlpatterns = [
    path('equipment/', views.EquipmentAndYardListView.as_view(), name='equipment-list'),
    path('equipment/add/<str:model>/', views.EquipmentCreateView.as_view(), name='equipment-add'),
    path('equipment/<str:model>/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
    path('yard/add/', views.YardCreateView.as_view(), name='yard-add'),
]