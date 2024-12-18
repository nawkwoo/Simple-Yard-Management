# apps/yms_edit/views.py

import csv
from io import TextIOWrapper
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    TemplateView, DetailView,
    CreateView, UpdateView, DeleteView,
    ListView
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.conf import settings

from .models import Yard, Site, Truck, Chassis, Container, Trailer, YardInventory
from .forms import (
    YardCreateForm, TruckForm, ChassisForm,
    ContainerForm, TrailerForm
)
from apps.yms_view.models import Transaction
from apps.yms_view.utils import process_order
from apps.dashboard.forms import CSVUploadForm

from geopy.geocoders import Nominatim


def get_lat_lon(address):
    # Geolocator 생성
    geolocator = Nominatim(user_agent="geoapi")

    # 주소를 위도, 경도로 변환
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


class EquipmentAndYardListView(TemplateView):
    """
    장비와 야드 목록을 보여주는 뷰.
    """
    template_name = 'yms_edit/equipment_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_types = ['truck', 'chassis', 'container', 'trailer']
        model_classes = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer,
        }
        equipments = {}
        selected_types = []

        # 모든 장비를 가져옵니다.
        for eq_type in equipment_types:
            model_class = model_classes[eq_type]
            equipments[eq_type + '_list'] = model_class.objects.all()

        # 야드 및 필터 파라미터를 가져옵니다.
        all_yards = Yard.objects.all()
        yards = all_yards

        yard_id = self.request.GET.get('yard')
        types = self.request.GET.get('types')

        if yard_id:
            try:
                yard_id_int = int(yard_id)
                yards = yards.filter(id=yard_id_int)
                for eq_type in equipment_types:
                    equipments[eq_type + '_list'] = equipments[eq_type + '_list'].filter(site__yard__id=yard_id_int)
            except ValueError:
                pass  # yard_id가 유효한 정수가 아닐 경우 필터를 적용하지 않음

        # 장비 유형 필터링
        if types:
            selected_types = types.split(',')
            for eq_type in equipment_types:
                if eq_type not in selected_types:
                    equipments[eq_type + '_list'] = equipments[eq_type + '_list'].none()
        else:
            # 선택된 타입이 없으면 모든 타입을 선택한 것으로 간주
            selected_types = equipment_types.copy()

        # 컨텍스트에 장비 리스트를 추가합니다.
        for eq_type in equipment_types:
            if eq_type == 'chassis':
                context['chassis'] = equipments[eq_type + '_list']
            else:
                context[eq_type + 's'] = equipments[eq_type + '_list']

        context['all_yards'] = all_yards
        context['yards'] = yards
        context['selected_yard_id'] = int(yard_id) if yard_id else None
        context['selected_types'] = selected_types
        context['all_types_selected'] = (len(selected_types) == len(equipment_types))

        # 구글 지도 API 키를 컨텍스트에 추가합니다.
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY  # settings.py에서 API 키 가져오기

        return context


class YardDetailView(DetailView):
    """야드 상세 보기 뷰"""
    model = Yard
    template_name = 'yms_edit/yard_detail.html'
    context_object_name = 'yard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 구글 지도 API 키를 컨텍스트에 추가
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        return context


class YardCreateView(CreateView):
    """
    야드 추가 뷰.
    """
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 구글 지도 API 키를 컨텍스트에 추가
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        equipment_types = form.cleaned_data.get('equipment_types', [])
        for equipment_type in equipment_types:
            capacity = Site.CAPACITY_MAPPING.get(equipment_type, 30)
            Site.objects.create(
                yard=self.object,
                equipment_type=equipment_type,
                capacity=capacity
            )
        messages.success(self.request, "야드와 사이트가 성공적으로 생성되었습니다.")
        return response

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class YardUpdateView(UpdateView):
    """
    야드 수정 뷰.
    """
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 구글 지도 API 키를 컨텍스트에 추가
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        equipment_types = form.cleaned_data.get('equipment_types', [])
        self.object.sites.all().delete()
        for equipment_type in equipment_types:
            capacity = Site.CAPACITY_MAPPING.get(equipment_type, 30)
            Site.objects.create(
                yard=self.object,
                equipment_type=equipment_type,
                capacity=capacity
            )
        messages.success(self.request, "야드와 사이트가 성공적으로 수정되었습니다.")
        return response

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class YardDeleteView(DeleteView):
    """
    야드 삭제 뷰.
    """
    model = Yard
    template_name = 'yms_edit/yard_confirm_delete.html'
    context_object_name = 'yard'

    def get_success_url(self):
        messages.success(self.request, "야드가 성공적으로 삭제되었습니다.")
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentDetailView(DetailView):
    """
    장비 상세 보기 뷰.
    """
    template_name = 'yms_edit/equipment_detail.html'
    context_object_name = 'equipment'

    def get_object(self):
        model = self.kwargs.get('model')
        pk = self.kwargs.get('pk')
        model_class = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer,
        }.get(model)
        if not model_class:
            raise Http404("잘못된 모델입니다.")
        return get_object_or_404(model_class, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()
        model = self.kwargs.get('model').capitalize()

        transactions = Transaction.objects.filter(
            equipment_type=model,
            truck_id=equipment.id
        ).order_by('-movement_time')

        context['transactions'] = transactions
        context['model_name'] = self.kwargs.get('model')
        return context


class EquipmentCreateView(CreateView):
    """
    장비 추가 뷰.
    """
    template_name = 'yms_edit/equipment_form.html'

    def find_smallest_missing(self, positions, max_value):
        if not positions:
            return 1
        position_set = set(positions)
        for i in range(1, max_value + 1):
            if i not in position_set:
                return i
        return max_value + 1

    def get_form_class(self):
        model = self.kwargs.get('model')
        form_class = {
            'truck': TruckForm,
            'chassis': ChassisForm,
            'container': ContainerForm,
            'trailer': TrailerForm,
        }.get(model)
        if not form_class:
            raise Http404("잘못된 모델입니다.")
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        model = self.kwargs.get('model').capitalize()
        kwargs['equipment_type'] = model
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        equipment = form.instance
        equipment_type = self.kwargs.get('model').capitalize()

        # --- 여기서부터 로그 추가 ---
        print("[DEBUG] form_valid in EquipmentCreateView called.")
        print(f"[DEBUG] equipment: {equipment}, equipment_id: {equipment.id}, equipment_type: {equipment_type}")

        yard = Yard.objects.filter(
            yard_id=equipment.site.yard.yard_id
        ).first()

        # yard 확인
        print(f"[DEBUG] Selected yard: {yard} (ID: {yard.id if yard else 'None'})")

        equipment_capcity = Site.objects.filter(
            yard_id=yard.id,
            equipment_type=equipment_type
        ).first().capacity

        positions = YardInventory.objects.filter(
            yard_id=yard.id,
            equipment_type=equipment_type,
            is_available=True
        ).values_list('position', flat=True)

        # positions 확인
        print(f"[DEBUG] Existing positions in yard {yard.id} for {equipment_type}: {list(positions)}")

        position = self.find_smallest_missing(positions, equipment_capcity)
        print(f"[DEBUG] Selected position: {position}")

        # YardInventory 생성 직전 로그
        print(f"[DEBUG] Creating YardInventory with equipment_id={equipment.id}, equipment_type={equipment_type}, yard_id={yard.id}")

        YardInventory.objects.create(
            yard=yard,
            equipment_type=equipment_type,
            equipment_id=equipment.id,  # Equipment의 ID 사용
            is_available=equipment.is_active,
            position=position
        )
        # --- 로그 추가 끝 ---

        messages.success(
            self.request,
            f"{equipment_type} 장비가 성공적으로 추가되었습니다."
        )
        return response

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentUpdateView(UpdateView):
    """
    장비 수정 뷰.
    """
    template_name = 'yms_edit/equipment_form.html'

    def get_form_class(self):
        model = self.kwargs.get('model')
        form_class = {
            'truck': TruckForm,
            'chassis': ChassisForm,
            'container': ContainerForm,
            'trailer': TrailerForm,
        }.get(model)
        if not form_class:
            raise Http404("잘못된 모델입니다.")
        return form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        model = self.kwargs.get('model').capitalize()
        kwargs['equipment_type'] = model
        return kwargs

    def get_object(self):
        model = self.kwargs.get('model')
        pk = self.kwargs.get('pk')
        model_class = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer,
        }.get(model)
        if not model_class:
            raise Http404("잘못된 모델입니다.")
        return get_object_or_404(model_class, pk=pk)

    def form_valid(self, form):
        response = super().form_valid(form)
        equipment = form.instance
        print("[DEBUG] form_valid in EquipmentUpdateView called.")
        print(f"[DEBUG] Updating equipment: {equipment}, equipment_id: {equipment.id}")

        # YardInventory 업데이트 로직
        try:
            yard_inventory = YardInventory.objects.get(equipment_id=equipment.id)
            print("[DEBUG] Found YardInventory:", yard_inventory)
            yard_inventory.equipment_type = self.kwargs.get('model').capitalize()
            yard_inventory.is_available = equipment.is_active
            yard_inventory.save()
            print("[DEBUG] Updated YardInventory:", yard_inventory)
        except YardInventory.DoesNotExist:
            print("[DEBUG] YardInventory does not exist for this equipment. Consider creating one if needed.")
            messages.warning(
                self.request,
                "연결된 YardInventory가 없어 새로 생성이 필요합니다."
            )

        messages.success(
            self.request,
            f"{self.kwargs.get('model').capitalize()} 장비가 성공적으로 수정되었습니다."
        )
        return response

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentDeleteView(DeleteView):
    """
    장비 삭제 뷰.
    """
    template_name = 'yms_edit/equipment_confirm_delete.html'

    def get_object(self):
        model = self.kwargs.get('model')
        pk = self.kwargs.get('pk')
        model_class = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer,
        }.get(model)
        if not model_class:
            raise Http404("잘못된 모델입니다.")
        return get_object_or_404(model_class, pk=pk)

    def get_success_url(self):
        messages.success(self.request, "장비가 성공적으로 삭제되었습니다.")
        return reverse_lazy('yms_edit:equipment-list')
