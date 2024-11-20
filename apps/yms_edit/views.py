from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Yard, Site, Truck, Chassis, Container, Trailer
from .forms import YardCreateForm, TruckForm, ChassisForm, ContainerForm, TrailerForm


# --- Equipment and Yard List View ---
class EquipmentAndYardListView(ListView):
    template_name = 'yms_edit/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        trucks = Truck.objects.filter(is_active=True)
        chassis = Chassis.objects.filter(is_active=True)
        containers = Container.objects.filter(is_active=True)
        trailers = Trailer.objects.filter(is_active=True)
        yards = Yard.objects.filter(is_active=True)

        yard_id = self.request.GET.get('yard')
        types = self.request.GET.get('types')

        # 야드 필터링
        if yard_id:
            yards = yards.filter(id=yard_id)
            trucks = trucks.filter(site__yard_id=yard_id)
            chassis = chassis.filter(site__yard_id=yard_id)
            containers = containers.filter(site__yard_id=yard_id)
            trailers = trailers.filter(site__yard_id=yard_id)

        # 장비 타입 필터링
        if types:
            selected_types = types.split(',')
            trucks = trucks if 'truck' in selected_types else trucks.none()
            chassis = chassis if 'chassis' in selected_types else chassis.none()
            containers = containers if 'container' in selected_types else containers.none()
            trailers = trailers if 'trailer' in selected_types else trailers.none()
        return {
            'trucks': trucks,
            'chassis': chassis,
            'containers': containers,
            'trailers': trailers,
            'yards': yards,
        }

    def get_context_data(self, **kwargs):
        """컨텍스트에 데이터 추가"""
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())
        return context

# --- Yard Views ---
class YardCreateView(CreateView):
    """야드 추가 뷰"""
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

    def form_valid(self, form):
        """야드 및 사이트 생성"""
        response = super().form_valid(form)
        equipment_types = form.cleaned_data['equipment_types']
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
        """야드 및 사이트 업데이트"""
        response = super().form_valid(form)
        equipment_types = form.cleaned_data['equipment_types']
        self.object.sites.all().delete()
        for equipment_type in equipment_types:
            Site.objects.create(
                yard=self.object,
                equipment_type=equipment_type,
                capacity=Site.CAPACITY_MAPPING.get(equipment_type, 30)
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


# --- Equipment Views ---
from apps.yms_view.models import Transaction  # 트랜잭션 모델 임포트

class EquipmentDetailView(DetailView):
    """장비 상세 보기 뷰"""
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

        # 트랜잭션 필터링
        transactions = Transaction.objects.filter(order__equipment=equipment)
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
        site = form.cleaned_data['site']
        model_name = self.kwargs.get('model').capitalize()
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