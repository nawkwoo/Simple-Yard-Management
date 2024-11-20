from django.shortcuts import render
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.generic import ListView
from apps.dashboard.models import Order
from apps.yms_view.models import Transaction
from apps.yms_edit.models import Yard, YardInventory
from datetime import datetime


# --- 주문 처리 로직 ---
def process_order(order_id):
    """
    특정 주문을 처리하는 함수.
    - 출발 야드에서 장비를 제거하고 도착 야드에 추가.
    - 성공 시 트랜잭션 생성.
    """
    try:
        order = Order.objects.get(id=order_id)
        equipment = order.truck or order.chassis or order.container or order.trailer

        # 출발 야드에서 장비 확인
        inventory_item = YardInventory.objects.filter(
            yard=order.departure_yard,
            equipment_id=equipment.serial_number,
            is_available=True
        ).first()

        if not inventory_item:
            raise ValidationError(f"{equipment.serial_number}이 출발 위치 야드에 없습니다.")

        # 트랜잭션 생성
        Transaction.objects.create(
            equipment=equipment,
            departure_yard=order.departure_yard,
            arrival_yard=order.arrival_yard,
            details=f"장비 {equipment.serial_number} 이동 완료."
        )

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

        # 주문 상태 업데이트
        order.status = "COMPLETED"

    except ValidationError as e:
        # 실패 시 상태 및 에러 메시지 기록
        order.status = "FAILED"
        order.error_message = str(e)

    except Exception as e:
        # 일반적인 예외 처리
        order.status = "FAILED"
        order.error_message = f"처리 중 오류 발생: {str(e)}"

    finally:
        # 주문 상태 저장
        order.save()


# --- 트랜잭션 리스트 뷰 ---
class TransactionListView(ListView):
    """
    트랜잭션 기록을 출력하는 뷰.
    """
    model = Transaction
    template_name = "yms_view/transaction_list.html"
    context_object_name = "transactions"
    ordering = ["-movement_time"]

    def get_queryset(self):
        """
        쿼리셋 필터링 로직.
        """
        queryset = super().get_queryset()

        yard_id = self.request.GET.get('yard')  # 선택된 야드 ID
        start_date = self.request.GET.get('start_date')  # 시작일
        end_date = self.request.GET.get('end_date')  # 종료일
        serial_number = self.request.GET.get('serial_number')  # 장비 시리얼 번호

        if yard_id:
            queryset = queryset.filter(Q(departure_yard__id=yard_id) | Q(arrival_yard__id=yard_id))

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

        if serial_number:
            queryset = queryset.filter(equipment__serial_number__icontains=serial_number)

        return queryset

    def get_context_data(self, **kwargs):
        """
        추가적인 컨텍스트 데이터.
        """
        context = super().get_context_data(**kwargs)
        context["yards"] = Yard.objects.all()
        context["selected_yard"] = self.request.GET.get('yard')
        context["start_date"] = self.request.GET.get('start_date')
        context["end_date"] = self.request.GET.get('end_date')
        context["serial_number"] = self.request.GET.get('serial_number')
        return context