from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from apps.dashboard.models import Order
from apps.yms_view.models import Transaction
from apps.yms_edit.models import Yard, YardInventory, Truck, Chassis, Container, Trailer, Site
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

def process_order(order_id):
    """
    특정 주문을 처리하는 함수.
    - 출발 야드에서 장비를 제거하고 도착 야드에 추가.
    - 성공 시 트랜잭션 생성.
    """
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            driver = order.driver
            equipment = order.truck or order.chassis or order.container or order.trailer

            # 주문 유형 검증
            if not equipment and not driver.user.has_car:
                raise ValidationError("자가용이 없는 운전자는 차량이 필요합니다.")

            if order.trailer and order.chassis:
                raise ValidationError("트레일러와 샤시는 동시에 사용할 수 없습니다.")

            if order.chassis and not order.truck:
                raise ValidationError("샤시는 트럭과 함께 사용해야 합니다.")

            if order.container and not order.chassis:
                raise ValidationError("컨테이너는 샤시와 함께 사용해야 합니다.")

            # 출발 야드에서 장비 확인
            if equipment:
                inventory_item = YardInventory.objects.select_for_update().filter(
                    yard=order.departure_yard,
                    equipment_id=equipment.serial_number,
                    is_available=True
                ).first()

                if not inventory_item:
                    raise ValidationError(f"{equipment.serial_number}이 출발 위치 야드에 없습니다.")

                # 출발 야드에서 장비 제거
                inventory_item.is_available = False
                inventory_item.save()

                # 도착 야드에 장비 추가
                YardInventory.objects.create(
                    yard=order.arrival_yard,
                    equipment_type=equipment.__class__.__name__,
                    equipment_id=equipment.serial_number,
                    is_available=True
                )

            # 트랜잭션 생성
            Transaction.objects.create(
                equipment=equipment,
                departure_yard=order.departure_yard,
                arrival_yard=order.arrival_yard,
                details=f"장비 {equipment.serial_number} 이동 완료." if equipment else "자가용 이동 완료.",
                movement_time=timezone.now()
            )

            # 주문 상태 업데이트
            order.status = "COMPLETED"

    except ValidationError as e:
        order.status = "FAILED"
        order.error_message = str(e)

    except Exception as e:
        order.status = "FAILED"
        order.error_message = f"처리 중 오류 발생: {str(e)}"

    finally:
        order.save()


class TransactionListView(ListView):
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
                Q(equipment__truck__serial_number__icontains=serial_number) |
                Q(equipment__chassis__serial_number__icontains=serial_number) |
                Q(equipment__container__serial_number__icontains=serial_number) |
                Q(equipment__trailer__serial_number__icontains=serial_number)
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