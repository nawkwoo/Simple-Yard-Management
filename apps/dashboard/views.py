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
            # CSV 파일 읽기
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                # 각 행을 기반으로 Order 생성
                departure_yard = Yard.objects.filter(yard_id=row['출발위치']).first()
                arrival_yard = Yard.objects.filter(yard_id=row['도착위치']).first()
                driver = Driver.objects.filter(driver_id=row['운전자']).first()

                Order.objects.create(
                    truck=row.get('트럭'),
                    chassis=row.get('샤시'),
                    container=row.get('컨테이너'),
                    trailer=row.get('트레일러'),
                    driver=driver,
                    departure_time=row['출발시간'],
                    arrival_time=row['도착시간'],
                    departure_yard=departure_yard,
                    arrival_yard=arrival_yard,
                )
            messages.success(request, "CSV 파일이 성공적으로 업로드되었습니다.")
            return redirect('order_list')  # 업로드 완료 후 리다이렉트
        except Exception as e:
            messages.error(request, f"CSV 처리 중 오류 발생: {e}")
    
    return render(request, 'dashboard/upload_csv.html')

from django.views.generic import ListView

class OrderListView(ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    context_object_name = 'orders'