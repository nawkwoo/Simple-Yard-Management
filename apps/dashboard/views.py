# apps/dashboard/views.py

import csv
from io import TextIOWrapper
from django.shortcuts import render, redirect, reverse
from .models import Order
from apps.yms_edit.models import Yard, Driver, Truck, Chassis, Container, Trailer, YardInventory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.generic import ListView
from django.utils import timezone

from apps.yms_view.utils import process_order  # process_order 함수가 yms_view/utils.py에 있다고 가정

class OrderListView(ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    context_object_name = 'orders'

@login_required
def home(request):
    context = {
        'edit_url': reverse('yms_edit:equipment-list'),
        'manage_url': reverse('yms_view:transaction_list'),
        'order_url': reverse('dashboard:order_list'),
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "CSV 파일만 업로드할 수 있습니다.")
            return redirect('dashboard:upload_csv')

        decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        reader = csv.DictReader(decoded_file)
        success_count = 0
        error_messages = []

        for row_number, row in enumerate(reader, start=2):  # 헤더는 1행으로 가정
            try:
                # 필수 필드 검증
                required_fields = ['출발위치', '도착위치', '출발시간', '도착시간', '운전자']
                for field in required_fields:
                    if not row.get(field):
                        raise ValueError(f"필수 필드 '{field}'가 누락되었습니다.")

                # 데이터 가져오기
                truck_id = row.get('트럭') or None
                chassis_id = row.get('샤시') or None
                container_id = row.get('컨테이너') or None
                trailer_id = row.get('트레일러') or None
                driver_id = row.get('운전자')
                departure_time = row.get('출발시간')
                arrival_time = row.get('도착시간')

                # 운전자 검증
                driver = Driver.objects.filter(driver_id=driver_id).first()
                if not driver:
                    raise ValueError(f"운전자 {driver_id}가 존재하지 않습니다.")

                # 주문 유형 검증
                if not truck_id and not driver.has_personal_vehicle:
                    raise ValueError(f"운전자 {driver_id}는 자가용이 없으므로 트럭이 필요합니다.")

                if trailer_id and chassis_id:
                    raise ValueError("트레일러와 샤시는 동시에 선택할 수 없습니다.")

                if chassis_id and not truck_id:
                    raise ValueError("샤시는 트럭이 있어야 선택할 수 있습니다.")

                if container_id and not chassis_id:
                    raise ValueError("컨테이너는 샤시가 있어야 선택할 수 있습니다.")

                # 출발 및 도착 야드 검증
                departure_yard = Yard.objects.filter(yard_id=row['출발위치']).first()
                arrival_yard = Yard.objects.filter(yard_id=row['도착위치']).first()
                if not departure_yard or not arrival_yard:
                    raise ValueError("출발위치 또는 도착위치가 유효하지 않습니다.")

                # 장비 객체 가져오기
                truck = Truck.objects.filter(serial_number=truck_id).first() if truck_id else None
                chassis = Chassis.objects.filter(serial_number=chassis_id).first() if chassis_id else None
                container = Container.objects.filter(serial_number=container_id).first() if container_id else None
                trailer = Trailer.objects.filter(serial_number=trailer_id).first() if trailer_id else None

                # 주문 생성 및 처리
                with transaction.atomic():
                    order = Order.objects.create(
                        truck=truck,
                        chassis=chassis,
                        container=container,
                        trailer=trailer,
                        driver=driver,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        departure_yard=departure_yard,
                        arrival_yard=arrival_yard,
                        status='PENDING'
                    )

                    # 주문 처리 함수 호출
                    process_order(order.id)

                success_count += 1

            except Exception as e:
                error_messages.append(f"Row {row_number}: {e}")

        if success_count > 0:
            messages.success(request, f"성공적으로 {success_count}개의 주문을 업로드했습니다.")
        if error_messages:
            for error in error_messages:
                messages.error(request, error)

        return redirect('dashboard:order_list')

    return render(request, 'dashboard/upload_csv.html')
