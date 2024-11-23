import csv
from django.shortcuts import render, redirect, reverse
from .models import Order
from apps.yms_edit.models import Yard, Driver
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.shortcuts import render

def index(request):
    return render(request, 'accounts/login.html')

@login_required
@login_required
def home(request):
    context = {
        'edit_url': reverse('edit:equipment-list'),
        'manage_url': reverse('view:view_page'),
        'order_url': reverse('dashboard:order_list'),
    }
    return render(request, 'dashboard/home.html', context)

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # 필요한 데이터 가져오기
                truck_id = row.get('트럭')
                chassis_id = row.get('샤시')
                container_id = row.get('컨테이너')
                trailer_id = row.get('트레일러')
                driver_id = row.get('운전자')

                # 운전자 검증
                driver = Driver.objects.filter(driver_id=driver_id).first()
                if not driver:
                    raise ValueError(f"운전자 {driver_id}가 존재하지 않습니다.")

                # 주문 유형 검증
                if not truck_id and not driver.has_personal_vehicle:
                    raise ValueError(f"운전자 {driver_id}는 자가용이 없으므로 주문이 유효하지 않습니다.")

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

                # 주문 생성
                Order.objects.create(
                    truck=Truck.objects.filter(serial_number=truck_id).first() if truck_id else None,
                    chassis=Chassis.objects.filter(serial_number=chassis_id).first() if chassis_id else None,
                    container=Container.objects.filter(serial_number=container_id).first() if container_id else None,
                    trailer=Trailer.objects.filter(serial_number=trailer_id).first() if trailer_id else None,
                    driver=driver,
                    departure_time=row['출발시간'],
                    arrival_time=row['도착시간'],
                    departure_yard=departure_yard,
                    arrival_yard=arrival_yard,
                )

            messages.success(request, "CSV 파일이 성공적으로 업로드되었습니다.")
            return redirect('dashboard:order_list')

        except Exception as e:
            messages.error(request, f"CSV 처리 중 오류 발생: {e}")
    
    return render(request, 'dashboard/upload_csv.html')

from django.views.generic import ListView

class OrderListView(ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    context_object_name = 'orders'