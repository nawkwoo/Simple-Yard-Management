# apps/yms_view/views.py

from django.views.generic import ListView
from .models import Transaction
from django.db.models import Q
from datetime import datetime
from .utils import process_order  # process_order 함수 임포트

from apps.yms_edit.models import Yard, Site, Truck, Chassis, Container, Trailer  # Yard 모델 임포트 추가

from django.contrib.auth.mixins import LoginRequiredMixin  # LoginRequiredMixin 임포트

class TransactionListView(LoginRequiredMixin, ListView):
    """
    트랜잭션 기록 및 선택된 야드 장비 정보를 출력하는 뷰.
    """
    model = Transaction
    template_name = "yms_view/transaction_list.html"
    context_object_name = "transactions"
    ordering = ["-movement_time"]

    def get_queryset(self):
        """
        트랜잭션 목록 필터링
        """
        queryset = super().get_queryset()
        yard_id = self.request.GET.get('yard')
        if yard_id:
            queryset = queryset.filter(Q(departure_yard__id=yard_id) | Q(arrival_yard__id=yard_id))

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(movement_time__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(movement_time__lte=end_date)
            except ValueError:
                pass

        serial_number = self.request.GET.get('serial_number')
        if serial_number:
            queryset = queryset.filter(
                Q(equipment_type='Truck', equipment__in=Truck.objects.filter(serial_number__icontains=serial_number).values_list('id', flat=True)) |
                Q(equipment_type='Chassis', equipment__in=Chassis.objects.filter(serial_number__icontains=serial_number).values_list('id', flat=True)) |
                Q(equipment_type='Container', equipment__in=Container.objects.filter(serial_number__icontains=serial_number).values_list('id', flat=True)) |
                Q(equipment_type='Trailer', equipment__in=Trailer.objects.filter(serial_number__icontains=serial_number).values_list('id', flat=True))
            )

        return queryset

    def get_context_data(self, **kwargs):
        """
        추가적인 컨텍스트 데이터를 템플릿에 전달.
        """
        context = super().get_context_data(**kwargs)

        # 기본 야드 설정
        yard_id = self.request.GET.get('yard')
        default_yard = Yard.objects.first()
        if not yard_id and default_yard:
            yard_id = default_yard.id

        # 야드 및 필터링 데이터
        context["yards"] = Yard.objects.all()
        context["selected_yard"] = yard_id
        context["start_date"] = self.request.GET.get('start_date', '')
        context["end_date"] = self.request.GET.get('end_date', '')
        context["serial_number"] = self.request.GET.get('serial_number', '')

        # 선택된 야드의 장비 정보
        selected_yard = Yard.objects.filter(id=yard_id).first() if yard_id else None
        if selected_yard:
            sites = Site.objects.filter(yard=selected_yard)

            # 각 장비 유형별 수량 및 range 리스트 생성
            inventory_status = []
            for equipment_type in ['Truck', 'Chassis', 'Container', 'Trailer']:
                model_class = {
                    'Truck': Truck,
                    'Chassis': Chassis,
                    'Container': Container,
                    'Trailer': Trailer,
                }[equipment_type]
                current_count = model_class.objects.filter(site__in=sites).count()
                capacity = Site.CAPACITY_MAPPING.get(equipment_type, 30)
                inventory_status.append({
                    'equipment_type': equipment_type,
                    'current_count': current_count,
                    'capacity': capacity,
                    'capacity_range': range(capacity),  # Range 전달
                })

            context["inventory_status"] = inventory_status
            context["selected_yard_name"] = selected_yard.yard_id
        else:
            context["inventory_status"] = []
            context["selected_yard_name"] = "없음"

        return context
