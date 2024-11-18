from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from .models import Yard, Site, Truck, Chassis, Container, Trailer
from .forms import YardCreateForm, TruckForm, ChassisForm, ContainerForm, TrailerForm


# --- Equipment and Yard List View ---
class EquipmentAndYardListView(ListView):
    """장비와 야드 목록 뷰"""
    template_name = 'yms_edit/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        """장비 및 야드 데이터 쿼리셋"""
        return {
            'trucks': Truck.objects.filter(is_active=True),
            'chassis': Chassis.objects.filter(is_active=True),
            'containers': Container.objects.filter(is_active=True),
            'trailers': Trailer.objects.filter(is_active=True),
            'yards': Yard.objects.filter(is_active=True),
        }

    def get_context_data(self, **kwargs):
        """컨텍스트에 야드와 장비 데이터 추가"""
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())
        return context


# --- Yard Create View ---
class YardCreateView(CreateView):
    """야드 추가 뷰"""
    model = Yard
    form_class = YardCreateForm
    template_name = 'yms_edit/yard_form.html'

    def form_valid(self, form):
        print("Form is valid and processing...")
        response = super().form_valid(form)
        equipment_types = form.cleaned_data['equipment_types']
        for equipment_type in equipment_types:
            Site.objects.create(
                yard=self.object,
                equipment_type=equipment_type
            )
        messages.success(self.request, "야드와 사이트가 성공적으로 생성되었습니다.")
        print("Message added and redirecting...")
        return response
    
    def form_invalid(self, form):
        print("Form is invalid")
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        print("Redirecting to equipment list...")
        return reverse_lazy('yms_edit:equipment-list')


# --- Equipment Detail View ---
class EquipmentDetailView(DetailView):
    """장비 상세 보기 뷰"""
    template_name = 'yms_edit/equipment_detail.html'
    context_object_name = 'equipment'

    def get_object(self):
        """장비 객체 반환"""
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


# --- Equipment Create View ---
class EquipmentCreateView(CreateView):
    """장비 추가 뷰"""
    template_name = 'yms_edit/equipment_form.html'

    def get_form_class(self):
        """폼 클래스 동적 반환"""
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
        """유효성 검사 및 저장"""
        site = form.cleaned_data['site']
        model_name = self.kwargs.get('model').capitalize()
        if site.equipment_type != model_name:
            form.add_error('site', f"선택한 사이트는 {model_name} 장비를 지원하지 않습니다.")
            return self.form_invalid(form)
        messages.success(self.request, f"{model_name} 장비가 성공적으로 추가되었습니다.")
        return super().form_valid(form)

    def get_success_url(self):
        """이큅먼트 및 야드 리스트 페이지로 리다이렉션"""
        return reverse_lazy('yms_edit:equipment-list')