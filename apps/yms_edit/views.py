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

from .models import Yard, Site, Truck, Chassis, Container, Trailer
from .forms import (
    YardCreateForm, TruckForm, ChassisForm,
    ContainerForm, TrailerForm
)
from apps.yms_view.models import Transaction
from apps.yms_view.utils import process_order
from apps.dashboard.forms import CSVUploadForm


class EquipmentAndYardListView(TemplateView):
    """
    장비와 야드 목록을 보여주는 뷰.
    """
    template_name = 'yms_edit/equipment_list.html'

    def get_context_data(self, **kwargs):
        """
        장비 유형별로 활성화된 장비를 필터링하여 컨텍스트에 추가합니다.
        또한, 야드 필터링 및 장비 유형 필터링을 적용합니다.
        """
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
            equipments[eq_type + '_list'] = model_class.objects.filter(is_active=True)

        # 야드 및 필터 파라미터를 가져옵니다.
        all_yards = Yard.objects.filter(is_active=True)
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
                pass  # yard_id가 유효한 정수가 아닐 경우 필터를 적용하지 않습니다.

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
        """
        폼이 유효할 때, 야드와 관련된 사이트를 생성합니다.
        """
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
        """
        폼이 유효할 때, 기존 사이트를 삭제하고 새 사이트를 생성합니다.
        """
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
        """
        URL 파라미터에 따라 해당 장비 객체를 반환합니다.
        """
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
        """
        장비와 관련된 트랜잭션 데이터를 컨텍스트에 추가합니다.
        """
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()
        model = self.kwargs.get('model').capitalize()

        # 트랜잭션 필터링: equipment_type과 equipment id를 기준으로 필터링
        transactions = Transaction.objects.filter(
            equipment_type=model,
            equipment=equipment.id
        ).order_by('-movement_time')

        context['transactions'] = transactions
        context['model_name'] = self.kwargs.get('model')
        return context


class EquipmentCreateView(CreateView):
    """
    장비 추가 뷰.
    """
    template_name = 'yms_edit/equipment_form.html'

    def get_form_class(self):
        """
        URL 파라미터에 따라 적절한 폼 클래스를 반환합니다.
        """
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
        """
        폼에 equipment_type을 전달합니다.
        """
        kwargs = super().get_form_kwargs()
        model = self.kwargs.get('model').capitalize()
        kwargs['equipment_type'] = model
        return kwargs

    def form_valid(self, form):
        """
        폼이 유효할 때, 성공 메시지를 추가합니다.
        """
        messages.success(
            self.request,
            f"{self.kwargs.get('model').capitalize()} 장비가 성공적으로 추가되었습니다."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentUpdateView(UpdateView):
    """
    장비 수정 뷰.
    """
    template_name = 'yms_edit/equipment_form.html'

    def get_form_class(self):
        """
        URL 파라미터에 따라 적절한 폼 클래스를 반환합니다.
        """
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
        """
        폼에 equipment_type을 전달합니다.
        """
        kwargs = super().get_form_kwargs()
        model = self.kwargs.get('model').capitalize()
        kwargs['equipment_type'] = model
        return kwargs

    def get_object(self):
        """
        URL 파라미터에 따라 해당 장비 객체를 반환합니다.
        """
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
        """
        폼이 유효할 때, 성공 메시지를 추가합니다.
        """
        messages.success(
            self.request,
            f"{self.kwargs.get('model').capitalize()} 장비가 성공적으로 수정되었습니다."
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentDeleteView(DeleteView):
    """
    장비 삭제 뷰.
    """
    template_name = 'yms_edit/equipment_confirm_delete.html'

    def get_object(self):
        """
        URL 파라미터에 따라 해당 장비 객체를 반환합니다.
        """
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
        """
        삭제 후 성공 메시지를 추가하고, 장비 목록 페이지로 리디렉션합니다.
        """
        messages.success(self.request, "장비가 성공적으로 삭제되었습니다.")
        return reverse_lazy('yms_edit:equipment-list')
