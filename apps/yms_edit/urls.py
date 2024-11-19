from django.urls import path
from . import views

app_name = 'yms_edit'

urlpatterns = [
    # Equipment and Yard List
    path('equipment/', views.EquipmentAndYardListView.as_view(), name='equipment-list'),

    # Yard CRUD
    path('yard/add/', views.YardCreateView.as_view(), name='yard-add'),
    path('yard/<int:pk>/', views.YardDetailView.as_view(), name='yard-detail'),
    path('yard/<int:pk>/edit/', views.YardUpdateView.as_view(), name='yard-update'),
    path('yard/<int:pk>/delete/', views.YardDeleteView.as_view(), name='yard-delete'),
    
    # Equipment CRUD
    path('equipment/add/<str:model>/', views.EquipmentCreateView.as_view(), name='equipment-add'),
    path('equipment/<str:model>/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment-detail'),
    path('equipment/<str:model>/<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment-edit'),
    path('equipment/<str:model>/<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment-delete'),
]