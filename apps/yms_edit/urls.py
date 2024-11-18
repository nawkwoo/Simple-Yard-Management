from django.urls import path
from . import views

app_name = 'yms_edit'

urlpatterns = [
    # Default View for Editing
    path('', views.edit_view, name='edit_view'),

    # Division URLs
    path('divisions/', views.DivisionListView.as_view(), name='division-list'),
    path('divisions/<int:pk>/', views.DivisionDetailView.as_view(), name='division-detail'),
    path('divisions/create/', views.DivisionCreateView.as_view(), name='division-create'),
    path('divisions/<int:pk>/update/', views.DivisionUpdateView.as_view(), name='division-update'),
    path('divisions/<int:pk>/delete/', views.DivisionDeleteView.as_view(), name='division-delete'),

    # Yard URLs
    path('yards/', views.YardListView.as_view(), name='yard-list'),
    path('yards/<int:pk>/', views.YardDetailView.as_view(), name='yard-detail'),
    path('yards/create/', views.YardCreateView.as_view(), name='yard-create'),
    path('yards/<int:pk>/update/', views.YardUpdateView.as_view(), name='yard-update'),
    path('yards/<int:pk>/delete/', views.YardDeleteView.as_view(), name='yard-delete'),

    # Site URLs
    path('sites/', views.SiteListView.as_view(), name='site-list'),
    path('sites/<int:pk>/', views.SiteDetailView.as_view(), name='site-detail'),
    path('sites/create/', views.SiteCreateView.as_view(), name='site-create'),
    path('sites/<int:pk>/update/', views.SiteUpdateView.as_view(), name='site-update'),
    path('sites/<int:pk>/delete/', views.SiteDeleteView.as_view(), name='site-delete'),

    # Driver URLs
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', views.DriverDetailView.as_view(), name='driver-detail'),
    path('drivers/create/', views.DriverCreateView.as_view(), name='driver-create'),
    path('drivers/<int:pk>/update/', views.DriverUpdateView.as_view(), name='driver-update'),
    path('drivers/<int:pk>/delete/', views.DriverDeleteView.as_view(), name='driver-delete'),

    # Truck URLs
    path('trucks/', views.TruckListView.as_view(), name='truck-list'),
    path('trucks/create/', views.TruckCreateView.as_view(), name='truck-create'),
    path('trucks/<int:pk>/update/', views.TruckCreateView.as_view(), name='truck-update'),
    path('trucks/<int:pk>/delete/', views.TruckCreateView.as_view(), name='truck-delete'),

    # Chassis URLs
    path('chassis/', views.ChassisListView.as_view(), name='chassis-list'),
    path('chassis/create/', views.ChassisCreateView.as_view(), name='chassis-create'),
    path('chassis/<int:pk>/update/', views.ChassisCreateView.as_view(), name='chassis-update'),
    path('chassis/<int:pk>/delete/', views.ChassisCreateView.as_view(), name='chassis-delete'),

    # Container URLs
    path('containers/', views.ContainerListView.as_view(), name='container-list'),
    path('containers/create/', views.ContainerCreateView.as_view(), name='container-create'),
    path('containers/<int:pk>/update/', views.ContainerCreateView.as_view(), name='container-update'),
    path('containers/<int:pk>/delete/', views.ContainerCreateView.as_view(), name='container-delete'),

    # Trailer URLs
    path('trailers/', views.TrailerListView.as_view(), name='trailer-list'),
    path('trailers/create/', views.TrailerCreateView.as_view(), name='trailer-create'),
    path('trailers/<int:pk>/update/', views.TrailerCreateView.as_view(), name='trailer-update'),
    path('trailers/<int:pk>/delete/', views.TrailerCreateView.as_view(), name='trailer-delete'),
]