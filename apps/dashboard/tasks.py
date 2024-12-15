# apps/dashboard/tasks.py
import threading
import time
from django.db import connection
from datetime import datetime, timezone

from apps.yms_edit.models import Site, Truck, Chassis, Container, Trailer, YardInventory
from apps.yms_view.models import Transaction


class OrderTableMonitor:
    """
    Order 테이블을 주기적으로 조회하는 모니터 클래스
    """
    def __init__(self, interval=10):
        self.interval = interval  # 조회 간격 (초 단위)
        self.thread = None
        self.running = False

    def start(self):
        """
        모니터링 스레드를 시작합니다.
        """
        if self.thread is None:
            self.running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            print("Order monitoring thread started.")

    def stop(self):
        """
        모니터링 스레드를 중지합니다.
        """
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None
            print("Order monitoring thread stopped.")

    def equipment_delete(self, order):
        if order.truck:
            truckObject = order.truck
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=truckObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.delete()

        if order.chassis:
            chassisObject = order.chassis
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=chassisObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.delete()

        if order.container:
            containerObject = order.container
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=containerObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.delete()

        if order.trailer:
            trailerObject = order.trailer
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=trailerObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.delete()

    def equipment_active(self, order, activate=False):
        if order.truck:
            order.truck.is_active = activate
            order.truck.save()

        if order.chassis:
            order.chassis.is_active = activate
            order.chassis.save()

        if order.container:
            order.container.is_active = activate
            order.container.save()

        if order.trailer:
            order.trailer.is_active = activate
            order.trailer.save()

    def inventory_equipment_inactive(self, order):
        if order.truck:
            truckObject = order.truck
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=truckObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.is_available = False
                inventory_item.save()

        if order.chassis:
            chassisObject = order.chassis
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=chassisObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.is_available = False
                inventory_item.save()

        if order.container:
            containerObject = order.container
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=containerObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.is_available = False
                inventory_item.save()

        if order.trailer:
            trailerObject = order.trailer
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=trailerObject.id,
                is_available=True
            ).first()
            if inventory_item:
                inventory_item.is_available = False
                inventory_item.save()

    def find_smallest_missing(self, positions, max_value):
        if not positions:
            return 1  # If the list is empty, return 1

        position_set = set(positions)  # Convert list to a set for fast lookup

        # Iterate from 1 to max_value to find the first missing number
        for i in range(1, max_value + 1):
            if i not in position_set:
                return i

        # If no missing number is found, return the next integer after max_value
        return max_value + 1

    def inventory_equipment_move(self, order):
        if order.truck:
            truck_capcity = Site.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Truck'
            ).first().capacity

            positions = YardInventory.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Truck',
                is_available=True
            ).values_list('position', flat=True)
            position = self.find_smallest_missing(positions, truck_capcity)

            truckObject = order.truck
            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=truckObject.id,
                is_available=False
            ).first()
            if inventory_item:
                inventory_item.yard_id = order.arrival_yard_id
                inventory_item.is_available = True
                inventory_item.position = position
                inventory_item.save()

        if order.chassis:
            chassisObject = order.chassis
            chassis_capcity = Site.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Chassis'
            ).first().capacity
            positions = YardInventory.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Chassis',
                is_available=True
            ).values_list('position', flat=True)
            position = self.find_smallest_missing(positions, chassis_capcity)

            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=chassisObject.id,
                is_available=False
            ).first()
            if inventory_item:
                inventory_item.yard_id = order.arrival_yard_id
                inventory_item.is_available = True
                inventory_item.position = position
                inventory_item.save()

        if order.container:
            containerObject = order.container
            container_capcity = Site.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Container'
            ).first().capacity
            positions = YardInventory.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Container',
                is_available=True
            ).values_list('position', flat=True)
            position = self.find_smallest_missing(positions, container_capcity)

            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=containerObject.id,
                is_available=False
            ).first()
            if inventory_item:
                inventory_item.yard_id = order.arrival_yard_id
                inventory_item.is_available = True
                inventory_item.position = position
                inventory_item.save()

        if order.trailer:
            trailerObject = order.trailer
            trailer_capcity = Site.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Trailer'
            ).first().capacity
            positions = YardInventory.objects.filter(
                yard_id=order.arrival_yard_id,
                equipment_type='Trailer',
                is_available=True
            ).values_list('position', flat=True)
            position = self.find_smallest_missing(positions, trailer_capcity)

            inventory_item = YardInventory.objects.filter(
                yard_id=order.departure_yard_id,
                equipment_id=trailerObject.id,
                is_available=False
            ).first()
            if inventory_item:
                inventory_item.yard_id = order.arrival_yard_id
                inventory_item.is_available = True
                inventory_item.position = position
                inventory_item.save()

    def equipment_move(self, order):
        if order.truck:
            site_id = Site.objects.get(
                yard_id=order.arrival_yard_id,  # Yard 모델의 yard_id 필드와 필터
                equipment_type='Truck'  # equipment_type 필터
            ).id
            order.truck.site_id = site_id
            order.truck.is_active = True
            order.truck.save()

        if order.chassis:
            site_id = Site.objects.get(
                yard_id=order.arrival_yard_id,  # Yard 모델의 yard_id 필드와 필터
                equipment_type='Chassis'  # equipment_type 필터
            ).id
            order.chassis.site_id = site_id
            order.chassis.is_active = True
            order.chassis.save()

        if order.container:
            site_id = Site.objects.get(
                yard_id=order.arrival_yard_id,  # Yard 모델의 yard_id 필드와 필터
                equipment_type='Container'  # equipment_type 필터
            ).id            
            order.container.site_id = site_id
            order.container.is_active = True
            order.container.save()

        if order.trailer:
            site_id = Site.objects.get(
                yard_id=order.arrival_yard_id,  # Yard 모델의 yard_id 필드와 필터
                equipment_type='Trailer'  # equipment_type 필터
            ).id                
            order.trailer.site_id = site_id
            order.trailer.is_active = True
            order.trailer.save()


    def run(self):
        """
        주기적으로 Order 테이블을 조회하는 함수
        """
        from apps.dashboard.models import Order  # 여기에서 임포트
        while self.running:
            try:
                print("Fetching orders...")
                # ORM을 사용해 Order 테이블 조회
                orders = Order.objects.all()
                for order in orders:
                    if (order.status_move == order.MOVE_STATUS_PENDING or order.status_move == order.MOVE_STATUS_DEPARTURED) and order.status == order.STATUS_COMPLETED:
                        # 현재 시간과 주문의 출발/도착 시간 비교
                        # 현재 UTC 시간
                        current_time = datetime.now(timezone.utc)
                        has_departed = order.departure_time < current_time
                        has_arrived = order.arrival_time < current_time
                        print(f"출발 시간 경과: {has_departed}")
                        print(f"도착 시간 경과: {has_arrived}")
                        print(f"Order ID: {order.id}, Status: {order.status}, currentTime: {current_time}, departureTime: {order.departure_time}, arrivalTime: {order.arrival_time}")

                        if has_departed:    # 주문 레코드에세 출발 시간이 경과한 경우
                            # 출발 야드에서 장비 제거
                            # inventory에서 equipment 비활성 화
                            self.inventory_equipment_inactive(order)
                            # 장비 비활성화
                            self.equipment_active(order, False)

                            if order.status_move == order.MOVE_STATUS_PENDING:
                                # 트랜잭션 생성
                                transaction, created = Transaction.objects.get_or_create(
                                    order_id=order.id,
                                    defaults={
                                        "equipment_type": order.truck.__class__.__name__ if order.truck else "PersonalVehicle",
                                        "truck": order.truck if isinstance(order.truck, Truck) else None,
                                        "chassis": order.chassis if isinstance(order.chassis, Chassis) else None,
                                        "container": order.container if isinstance(order.container, Container) else None,
                                        "trailer": order.trailer if isinstance(order.trailer, Trailer) else None,
                                        "departure_yard": order.departure_yard,
                                        "arrival_yard": order.arrival_yard,
                                        "details": f"장비 {order.truck.serial_number} Truck 이동 시작." if order.truck else "자가용 이동 시작.",
                                        "movement_time": datetime.now(timezone.utc),
                                    },
                                )
                                order.status_move = order.MOVE_STATUS_DEPARTURED
                                order.save()

                                if created:
                                    print(f"Transaction created for Order ID: {order.id}")
                                else:
                                    print(f"Transaction already exists for Order ID: {order.id}")

                        if has_arrived: # 주문 레코드에세 대한 도착 시간이 경과한 경우
                            self.inventory_equipment_move(order)
                            self.equipment_move(order)
                            if order.status_move == order.MOVE_STATUS_DEPARTURED:
                                # 트랜잭션 생성
                                created = Transaction.objects.create(
                                    order_id=order.id,
                                    equipment_type=order.truck.__class__.__name__ if order.truck else "PersonalVehicle",
                                    truck=order.truck if isinstance(order.truck, Truck) else None,
                                    chassis=order.chassis if isinstance(order.chassis, Chassis) else None,
                                    container=order.container if isinstance(order.container, Container) else None,
                                    trailer=order.trailer if isinstance(order.trailer, Trailer) else None,
                                    departure_yard=order.departure_yard,
                                    arrival_yard=order.arrival_yard,
                                    details=f"장비 {order.truck.serial_number} Truck 이동 완료." if order.truck else "자가용 이동 완료.",
                                    movement_time=datetime.now(timezone.utc)
                                )
                                order.status_move = order.MOVE_STATUS_ARRIVED
                                order.save()                            

                                if created:
                                    print(f"Transaction created for Order ID: {order.id}")
                                else:
                                    print(f"Transaction already exists for Order ID: {order.id}")

                # DB connection 상태 확인
                if connection.connection and not connection.is_usable():
                    connection.close()

                print(f"OrderTableMonitor thread is running.......................")
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error while monitoring orders: {e}")
                time.sleep(self.interval)



