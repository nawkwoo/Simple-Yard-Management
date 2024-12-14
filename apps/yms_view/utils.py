# apps/yms_view/utils.py

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.dashboard.models import Order
from apps.yms_edit.models import Yard, YardInventory, Truck, Chassis, Container, Trailer
from .models import Transaction
import logging

logger = logging.getLogger('yms_view')


def process_order(order_id):
    """
    특정 주문을 처리하는 함수.
    - 출발 야드에서 장비를 제거하고 도착 야드에 추가.
    - 성공 시 트랜잭션 생성.
    """
    try:
        with transaction.atomic():
            # 주문 조회 및 잠금
            order = Order.objects.select_for_update().get(id=order_id)
            driver = order.driver  # Driver 모델이 CustomUser와 연결되어 있다고 가정
            profile = getattr(driver, 'profile', None)

            if not profile:
                raise ValidationError("운전사의 프로필이 존재하지 않습니다.")

            equipment = order.truck or order.chassis or order.container or order.trailer

            # 주문 유형 검증
            if not equipment and not profile.has_car:
                raise ValidationError("자가용이 없는 운전자는 차량이 필요합니다.")

            if order.trailer and order.chassis:
                raise ValidationError("트레일러와 샤시는 동시에 사용할 수 없습니다.")

            if order.chassis and not order.truck:
                raise ValidationError("샤시는 트럭과 함께 사용해야 합니다.")

            if order.container and not order.chassis:
                raise ValidationError("컨테이너는 샤시와 함께 사용해야 합니다.")

            if order.truck:
                truckObject = Truck.objects.get(serial_number=order.truck.serial_number)
                inventory_item = YardInventory.objects.select_for_update().filter(
                    yard_id=order.departure_yard.id,
                    equipment_id=truckObject.id,
                    is_available=True
                ).first()

                if not inventory_item:
                    raise ValidationError(f"Truck 시리얼넘버({equipment.serial_number})가 출발 위치 야드에 없습니다.")

            if order.chassis:
                chassisObject = Chassis.objects.get(serial_number=order.chassis.serial_number)
                inventory_item = YardInventory.objects.select_for_update().filter(
                    yard_id=order.departure_yard.id,
                    equipment_id=chassisObject.id,
                    is_available=True
                ).first()

                if not inventory_item:
                    raise ValidationError(f"Chassis 시리얼넘버({equipment.serial_number})가 출발 위치 야드에 없습니다.")
                
            if order.container:
                containerObject = Container.objects.get(serial_number=order.container.serial_number)
                inventory_item = YardInventory.objects.select_for_update().filter(
                    yard_id=order.departure_yard.id,
                    equipment_id=containerObject.id,
                    is_available=True
                ).first()

                if not inventory_item:
                    raise ValidationError(f"Container 시리얼넘버({equipment.serial_number})가 출발 위치 야드에 없습니다.")
                
            if order.trailer:
                trailerObject = Trailer.objects.get(serial_number=order.trailer.serial_number)
                inventory_item = YardInventory.objects.select_for_update().filter(
                    yard_id=order.departure_yard.id,
                    equipment_id=trailerObject.id,
                    is_available=True
                ).first()

                if not inventory_item:
                    raise ValidationError(f"Trailer 시리얼넘버({equipment.serial_number})가 출발 위치 야드에 없습니다.")

            order.status = "COMPLETED"
            order.error_message = None  # 오류 메시지 초기화
            logger.info(f"Order {order_id} processed successfully.")

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        raise ValidationError("존재하지 않는 주문입니다.")

    except ValidationError as e:
        order.status = "FAILED"
        order.error_message = str(e)
        logger.warning(f"ValidationError while processing order {order_id}: {e}")
        raise

    except Exception as e:
        order.status = "FAILED"
        order.error_message = f"처리 중 오류 발생: {str(e)}"
        logger.error(f"Unexpected error while processing order {order_id}: {e}")
        raise ValidationError(f"처리 중 오류 발생: {str(e)}")

    finally:
        order.save()
