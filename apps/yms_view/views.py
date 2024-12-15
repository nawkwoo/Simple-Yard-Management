# apps/yms_view/views.py

import json
from urllib.parse import parse_qs
from django.http import JsonResponse
from django.views.generic import ListView, View
from django.db.models import Q
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError

from .models import Transaction
from .utils import process_order
from apps.yms_edit.models import Yard, Site, Truck, Chassis, Container, Trailer, Division
from django.urls import reverse_lazy


class YardListView(View):
    def post(self, request, *args, **kwargs):
        post_data = request.body.decode('utf-8')

        # URL 파라미터를 파싱합니다.
        data = parse_qs(post_data)

        # 'division_name' 값을 가져옵니다.
        division_name = data.get('division_name', [None])[0]

        if not division_name:
            return JsonResponse({'error': 'division_name is required'}, status=400)

        # yard_prefix를 기준으로 Yard 모델에서 데이터를 가져옵니다.
        division_id = Division.objects.get(name=division_name).id
        yard_ids = list(Yard.objects.filter(division_id=division_id).values_list('yard_id', flat=True))

        # 결과를 JSON으로 반환합니다.
        return JsonResponse({'yard_ids': yard_ids}, status=200)
    
    def get(self, request, *args, **kwargs):
        # 'yard_id'를 querystring에서 가져옵니다.
        yard_id = request.GET.get('yard_id', None)

        if not yard_id:
            return JsonResponse({'error': 'yard_id is required'}, status=400)

        yard_id = Yard.objects.get(yard_id=yard_id).id
        # yard_id를 기준으로 Transaction을 필터링하고, Truck 모델을 함께 조인
        transactions_equipment_in = Transaction.objects.filter(
            Q(arrival_yard_id=yard_id)
        ).select_related('truck')  # 'truck'은 Transaction 모델에서 Truck 외래 키 필드 이름

        result_in = []
        for transaction in transactions_equipment_in:
            result_in.append({
                'movement_time': transaction.movement_time,
                'equipment_type': transaction.equipment_type,
                'truck_id': transaction.truck.truck_id if transaction.truck else None,
                'type': 'in'  # 'type' 필드 추가
            })

        # yard_id를 기준으로 Transaction을 필터링하고, Truck 모델을 함께 조인
        transactions_equipment_out = Transaction.objects.filter(
            Q(departure_yard_id=yard_id)
        ).select_related('truck')  # 'truck'은 Transaction 모델에서 Truck 외래 키 필드 이름
        result_out = []
        for transaction in transactions_equipment_out:
            result_out.append({
                'movement_time': transaction.movement_time,
                'equipment_type': transaction.equipment_type,
                'truck_id': transaction.truck.truck_id if transaction.truck else None,
                'type': 'out'  # 'type' 필드 추가
            })
        combined_result = result_in + result_out
        # 'movement_time'을 기준으로 오름차순으로 정렬합니다.
        combined_result_sorted = sorted(combined_result, key=lambda x: x['movement_time'])

        # 결과를 JSON으로 반환
        return JsonResponse({'transactions': combined_result_sorted}, status=200)

class TransactionListView(LoginRequiredMixin, ListView):
    """
    트랜잭션 기록 및 선택된 야드의 장비 정보를 출력하는 뷰.
    """
    model = Transaction
    template_name = "yms_view/yard_view.html"
    context_object_name = "transactions"
    ordering = ["-movement_time"]

    def get_queryset(self):
        """
        트랜잭션 목록을 필터링합니다.
        """
        queryset = super().get_queryset()
        yard_id = self.request.GET.get('yard')

        if yard_id:
            queryset = queryset.filter(
                Q(departure_yard__id=yard_id) | Q(arrival_yard__id=yard_id)
            )

        # 날짜 필터링
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(movement_time__gte=start_date_obj)
            except ValueError:
                messages.warning(self.request, "시작 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.")

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(movement_time__lte=end_date_obj)
            except ValueError:
                messages.warning(self.request, "종료 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.")

        # 일련번호 필터링
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
        추가적인 컨텍스트 데이터를 템플릿에 전달합니다.
        """
        context = super().get_context_data(**kwargs)

        # 필터링 관련 데이터
        yard_id = self.request.GET.get('yard')
        context["yards"] = Yard.objects.select_related('division').all().order_by('division__name', 'yard_id')
        context["divisions"] = Division.objects.all().order_by('name')
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
                    'capacity_range': range(capacity),
                })

            context["inventory_status"] = inventory_status
            context["selected_yard_name"] = selected_yard.yard_id

            # 장비 리스트 분류
            context["truck_equipments"] = Truck.objects.filter(site__in=sites).order_by('truck_id')
            context["chassis_equipments"] = Chassis.objects.filter(site__in=sites).order_by('chassis_id')
            context["container_equipments"] = Container.objects.filter(site__in=sites).order_by('container_id')
            context["trailer_equipments"] = Trailer.objects.filter(site__in=sites).order_by('trailer_id')

            # 각 장비 유형별 점유 수 계산
            context["truck_occupied_count"] = context["truck_equipments"].filter(is_occupied=True).count()
            context["chassis_occupied_count"] = context["chassis_equipments"].filter(is_occupied=True).count()
            context["container_occupied_count"] = context["container_equipments"].filter(is_occupied=True).count()
            context["trailer_occupied_count"] = context["trailer_equipments"].filter(is_occupied=True).count()
        else:
            context["inventory_status"] = []
            context["selected_yard_name"] = "없음"
            context["truck_equipments"] = Truck.objects.none()
            context["chassis_equipments"] = Chassis.objects.none()
            context["container_equipments"] = Container.objects.none()
            context["trailer_equipments"] = Trailer.objects.none()

            # 각 장비 유형별 점유 수 초기화
            context["truck_occupied_count"] = 0
            context["chassis_occupied_count"] = 0
            context["container_occupied_count"] = 0
            context["trailer_occupied_count"] = 0

        return context

from .forms import MoveEquipmentForm

class MoveEquipmentView(LoginRequiredMixin, View):
    """
    장비 이동을 처리하는 뷰.
    GET 요청: 이동 폼 표시
    POST 요청: 주문 처리 및 장비 이동
    """

    def get(self, request, *args, **kwargs):
        """
        GET 요청 시 장비 이동 폼을 표시합니다.
        """
        yards = Yard.objects.all()
        form = MoveEquipmentForm()
        return render(request, 'yms_view/yard_view.html', {'yards': yards, 'form': form})

    def post(self, request, *args, **kwargs):
        """
        POST 요청 시 주문을 처리하고 장비를 이동시킵니다.
        """
        form = MoveEquipmentForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            try:
                process_order(order_id=order_id)
                messages.success(request, "장비가 성공적으로 이동되었습니다.")
            except ValidationError as e:
                messages.error(request, f"장비 이동 중 오류가 발생했습니다: {str(e)}")
            except Exception as e:
                messages.error(request, f"장비 이동 중 예기치 않은 오류가 발생했습니다: {str(e)}")
        else:
            messages.error(request, "올바른 주문 ID를 입력하세요.")

        return redirect('yms_view:transaction-list')