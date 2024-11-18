from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Truck, Chassis, Container, Trailer


# --- Equipment List View ---
class EquipmentListView(ListView):
    """장비 목록 뷰"""
    model = Truck  # 기본적으로 Truck을 사용 (다른 장비도 추가)
    template_name = 'yms_edit/equipment_list.html'
    context_object_name = 'equipments'

    def get_queryset(self):
        """모든 장비를 포함하는 쿼리셋 반환"""
        trucks = Truck.objects.filter(is_active=True)
        chassis = Chassis.objects.filter(is_active=True)
        containers = Container.objects.filter(is_active=True)
        trailers = Trailer.objects.filter(is_active=True)
        return list(trucks) + list(chassis) + list(containers) + list(trailers)


# --- Equipment Detail View ---
class EquipmentDetailView(DetailView):
    """장비 상세 보기 뷰"""
    model = None  # 구체적인 모델은 get_object로 결정
    template_name = 'yms_edit/equipment_detail.html'
    context_object_name = 'equipment'

    def get_object(self, queryset=None):
        """URL에서 pk와 모델 이름을 가져와 해당 장비 반환"""
        pk = self.kwargs.get('pk')
        model = self.kwargs.get('model')
        model_class = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer
        }.get(model)

        if not model_class:
            raise ValueError("Invalid model type.")
        
        return get_object_or_404(model_class, pk=pk)


# --- Equipment Create View ---
class EquipmentCreateView(CreateView):
    """장비 추가 뷰"""
    model = Truck  # 기본적으로 Truck을 사용 (url에 따라 변경)
    template_name = 'yms_edit/equipment_form.html'
    fields = ['site', 'serial_number', 'image', 'is_active']

    def get_success_url(self):
        """생성 후 장비 목록으로 리디렉션"""
        return reverse_lazy('yms_edit:equipment-list')

    def get_context_data(self, **kwargs):
        """모델 이름에 따라 동적으로 제목 변경"""
        context = super().get_context_data(**kwargs)
        model = self.kwargs.get('model')
        context['model_name'] = model.capitalize() if model else 'Equipment'
        return context

    def get_form(self, form_class=None):
        """모델에 따라 동적으로 필드 설정"""
        model = self.kwargs.get('model')
        self.model = {
            'truck': Truck,
            'chassis': Chassis,
            'container': Container,
            'trailer': Trailer
        }.get(model, Truck)  # 기본은 Truck
        return super().get_form(form_class)