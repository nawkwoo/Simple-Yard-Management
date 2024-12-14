# apps/dashboard/tasks.py
import threading
import time
from django.db import connection
from datetime import datetime, timezone


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
                    # 현재 UTC 시간
                    current_time = datetime.now(timezone.utc)
                    has_departed = order.departure_time < current_time
                    has_arrived = order.arrival_time < current_time
                    print(f"출발 시간 경과: {has_departed}")
                    print(f"도착 시간 경과: {has_arrived}")
                    print(f"Order ID: {order.id}, Status: {order.status}, currentTime: {current_time}, departureTime: {order.departure_time}, arrivalTime: {order.arrival_time}")


                # DB connection 상태 확인
                if connection.connection and not connection.is_usable():
                    connection.close()

                print(f"OrderTableMonitor thread is running.......................")
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error while monitoring orders: {e}")
                time.sleep(self.interval)
