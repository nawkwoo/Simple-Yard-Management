from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import Division, Yard, Site, Driver, Truck, Chassis, Container, Trailer



def edit_view(request):
    # 기본 렌더링 템플릿 (yms_edit/edit_view.html)
    return render(request, 'yms_edit/edit_view.html')

# --- Division Views ---
class DivisionListView(ListView):
    model = Division
    template_name = "division_list.html"
    context_object_name = "divisions"

class DivisionDetailView(DetailView):
    model = Division
    template_name = "division_detail.html"
    context_object_name = "division"

class DivisionCreateView(CreateView):
    model = Division
    fields = ['name', 'full_name', 'is_active']
    template_name = "division_form.html"
    success_url = reverse_lazy('division-list')

class DivisionUpdateView(UpdateView):
    model = Division
    fields = ['name', 'full_name', 'is_active']
    template_name = "division_form.html"
    success_url = reverse_lazy('division-list')

class DivisionDeleteView(DeleteView):
    model = Division
    template_name = "division_confirm_delete.html"
    success_url = reverse_lazy('division-list')


# --- Yard Views ---
class YardListView(ListView):
    model = Yard
    template_name = "yard_list.html"
    context_object_name = "yards"

class YardDetailView(DetailView):
    model = Yard
    template_name = "yard_detail.html"
    context_object_name = "yard"

class YardCreateView(CreateView):
    model = Yard
    fields = ['division', 'yard_id', 'is_active']
    template_name = "yard_form.html"
    success_url = reverse_lazy('yard-list')

class YardUpdateView(UpdateView):
    model = Yard
    fields = ['division', 'yard_id', 'is_active']
    template_name = "yard_form.html"
    success_url = reverse_lazy('yard-list')

class YardDeleteView(DeleteView):
    model = Yard
    template_name = "yard_confirm_delete.html"
    success_url = reverse_lazy('yard-list')


# --- Site Views ---
class SiteListView(ListView):
    model = Site
    template_name = "site_list.html"
    context_object_name = "sites"

class SiteDetailView(DetailView):
    model = Site
    template_name = "site_detail.html"
    context_object_name = "site"

class SiteCreateView(CreateView):
    model = Site
    fields = ['yard', 'equipment_type', 'capacity', 'is_active']
    template_name = "site_form.html"
    success_url = reverse_lazy('site-list')

class SiteUpdateView(UpdateView):
    model = Site
    fields = ['yard', 'equipment_type', 'capacity', 'is_active']
    template_name = "site_form.html"
    success_url = reverse_lazy('site-list')

class SiteDeleteView(DeleteView):
    model = Site
    template_name = "site_confirm_delete.html"
    success_url = reverse_lazy('site-list')


# --- Driver Views ---
class DriverListView(ListView):
    model = Driver
    template_name = "driver_list.html"
    context_object_name = "drivers"

class DriverDetailView(DetailView):
    model = Driver
    template_name = "driver_detail.html"
    context_object_name = "driver"

class DriverCreateView(CreateView):
    model = Driver
    fields = ['user', 'driver_id', 'is_active']
    template_name = "driver_form.html"
    success_url = reverse_lazy('driver-list')

class DriverUpdateView(UpdateView):
    model = Driver
    fields = ['user', 'driver_id', 'is_active']
    template_name = "driver_form.html"
    success_url = reverse_lazy('driver-list')

class DriverDeleteView(DeleteView):
    model = Driver
    template_name = "driver_confirm_delete.html"
    success_url = reverse_lazy('driver-list')


# --- Equipment Views (Truck, Chassis, Container, Trailer) ---
class TruckListView(ListView):
    model = Truck
    template_name = "truck_list.html"
    context_object_name = "trucks"

class TruckCreateView(CreateView):
    model = Truck
    fields = ['site', 'truck_id', 'is_active']
    template_name = "truck_form.html"
    success_url = reverse_lazy('truck-list')


class ChassisListView(ListView):
    model = Chassis
    template_name = "chassis_list.html"
    context_object_name = "chassis_list"

class ChassisCreateView(CreateView):
    model = Chassis
    fields = ['site', 'chassis_id', 'type', 'is_active']
    template_name = "chassis_form.html"
    success_url = reverse_lazy('chassis-list')


class ContainerListView(ListView):
    model = Container
    template_name = "container_list.html"
    context_object_name = "containers"

class ContainerCreateView(CreateView):
    model = Container
    fields = ['site', 'container_id', 'size', 'type', 'is_active']
    template_name = "container_form.html"
    success_url = reverse_lazy('container-list')


class TrailerListView(ListView):
    model = Trailer
    template_name = "trailer_list.html"
    context_object_name = "trailers"

class TrailerCreateView(CreateView):
    model = Trailer
    fields = ['site', 'trailer_id', 'size', 'is_active']
    template_name = "trailer_form.html"
    success_url = reverse_lazy('trailer-list')