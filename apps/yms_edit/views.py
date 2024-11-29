from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Yard, Site, Truck, Chassis, Container, Trailer
from .forms import YardCreateForm, TruckForm, ChassisForm, ContainerForm, TrailerForm
from django.http import Http404

class EquipmentAndYardListView(TemplateView):
    template_name = 'yms_edit/equipment_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment_types = ['truck', 'chassis', 'container', 'trailer']
        equipments = {}
        for eq_type in equipment_types:
            model_class = {
                'truck': Truck,
                'chassis': Chassis,
                'container': Container,
                'trailer': Trailer,
            }[eq_type]
            equipments[eq_type + 's'] = model_class.objects.filter(is_active=True)

        yards = Yard.objects.filter(is_active=True)
        yard_id = self.request.GET.get('yard')
        types = self.request.GET.get('types')

        if yard_id:
            yards = yards.filter(id=yard_id)
            for eq_type in equipment_types:
                model_class = {
                    'truck': Truck,
                    'chassis': Chassis,
                    'container': Container,
                    'trailer': Trailer,
                }[eq_type]
                equipments[eq_type + 's'] = equipments[eq_type + 's'].filter(site__yard_id=yard_id)

        if types:
            selected_types = types.split(',')
            for eq_type in equipment_types:
                if eq_type not in selected_types:
                    equipments[eq_type + 's'] = model_class.objects.none()

        context['equipments'] = equipments
        context['yards'] = yards
        return context

class YardCreateView(CreateView):
    """야드 추가 뷰"""
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

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


class YardDetailView(DetailView):
    """야드 상세 보기 뷰"""
    model = Yard
    template_name = 'yms_edit/yard_detail.html'
    context_object_name = 'yard'


class YardUpdateView(UpdateView):
    """야드 수정 뷰"""
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

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
    """야드 삭제 뷰"""
    model = Yard
    template_name = 'yms_edit/yard_confirm_delete.html'
    context_object_name = 'yard'

    def get_success_url(self):
        messages.success(self.request, "야드가 성공적으로 삭제되었습니다.")
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentDetailView(DetailView):
    """장비 상세 보기 뷰"""
    template_name = 'yms_edit/equipment_detail.html'
    context_object_name = 'equipment'

    def get_object(self):
        """모델에 따라 장비 객체를 가져옵니다."""
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
        """추가 데이터를 컨텍스트에 전달"""
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()

        # 트랜잭션 필터링: GenericRelation 사용
        transactions = equipment.transactions.all()

        # 컨텍스트 업데이트
        context['transactions'] = transactions
        context['model_name'] = self.kwargs.get('model')
        return context


class EquipmentCreateView(CreateView):
    """장비 추가 뷰"""
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

    def form_valid(self, form):
        """사이트 용량 확인 및 검증"""
        site = form.cleaned_data['site']
        model_name = self.kwargs.get('model').capitalize()

        # 특정 장비 타입의 현재 수량 확인
        equipment_type_map = {
            'Truck': Truck,
            'Chassis': Chassis,
            'Container': Container,
            'Trailer': Trailer,
        }
        EquipmentModel = equipment_type_map.get(model_name)
        if not EquipmentModel:
            form.add_error('site', f"잘못된 장비 타입: {model_name}")
            return self.form_invalid(form)

        current_count = EquipmentModel.objects.filter(site=site).count()
        if current_count >= site.capacity:
            form.add_error('site', f"선택한 사이트는 최대 용량({site.capacity})을 초과했습니다.")
            return self.form_invalid(form)

        if site.equipment_type != model_name:
            form.add_error('site', f"선택한 사이트는 {model_name} 장비를 지원하지 않습니다.")
            return self.form_invalid(form)

        messages.success(self.request, f"{model_name} 장비가 성공적으로 추가되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentUpdateView(UpdateView):
    """장비 수정 뷰"""
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
        site = form.cleaned_data['site']
        model_name = self.kwargs.get('model').capitalize()
        equipment_type_map = {
            'Truck': Truck,
            'Chassis': Chassis,
            'Container': Container,
            'Trailer': Trailer,
        }
        EquipmentModel = equipment_type_map.get(model_name)
        if not EquipmentModel:
            form.add_error('site', f"잘못된 장비 타입: {model_name}")
            return self.form_invalid(form)

        if site.equipment_type != model_name:
            form.add_error('site', f"선택한 사이트는 {model_name} 장비를 지원하지 않습니다.")
            return self.form_invalid(form)

        messages.success(self.request, f"{model_name} 장비가 성공적으로 수정되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('yms_edit:equipment-list')


class EquipmentDeleteView(DeleteView):
    """장비 삭제 뷰"""
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