import csv
from apps.yms_edit.models import Truck, Chassis, Trailer, Yard, Driver
from apps.accounts.models import CustomUser
from datetime import datetime

# CSV 데이터
csv_data = """T1234,,C5678901,,D00001,2024-11-21T08:00:00,2024-11-21T10:00:00,YD01,YD02
,,C5678901,,D00002,2024-11-21T08:00:00,2024-11-21T10:00:00,YD01,YD02
,,,TR90001,D00003,2024-11-21T08:00:00,2024-11-21T10:00:00,YD01,YD02
,,,,D00004,2024-11-21T08:00:00,2024-11-21T10:00:00,YD01,YD02"""

# CSV 읽기
data = csv.reader(csv_data.splitlines())

# 첫 번째 줄은 열 이름이므로 건너뜁니다.
header = next(data)

# 데이터 주입
for row in data:
    truck_serial = row[0].strip() or None
    chassis_serial = row[1].strip() or None
    container_serial = row[2].strip() or None
    trailer_serial = row[3].strip() or None
    driver_id = row[4].strip()
    departure_time = datetime.fromisoformat(row[5])
    arrival_time = datetime.fromisoformat(row[6])
    departure_yard_id = row[7].strip()
    arrival_yard_id = row[8].strip()

    # 트럭
    if truck_serial:
        Truck.objects.get_or_create(serial_number=truck_serial, defaults={
            'truck_id': truck_serial[-4:],  # ID를 시리얼 번호 마지막 4자리로 설정
            'site': None  # 사이트 정보는 수동으로 추가해야 함
        })

    # 샤시
    if chassis_serial:
        Chassis.objects.get_or_create(serial_number=chassis_serial, defaults={
            'chassis_id': chassis_serial[:4],  # ID를 시리얼 번호 첫 4자리로 설정
            'type': 'Regular',  # 기본 샤시 타입 설정
            'site': None  # 사이트 정보는 수동으로 추가해야 함
        })

    # 트레일러
    if trailer_serial:
        Trailer.objects.get_or_create(serial_number=trailer_serial, defaults={
            'trailer_id': trailer_serial[:10],  # ID를 시리얼 번호 첫 10자리로 설정
            'size': '53',  # 기본 트레일러 크기 설정
            'site': None  # 사이트 정보는 수동으로 추가해야 함
        })

    # 운전자
    if driver_id:
        user, _ = CustomUser.objects.get_or_create(username=f"user_{driver_id}", defaults={
            'user_type': 'staff',
            'has_car': (driver_id == 'D00004'),  # D00004만 자가용 있음
        })
        Driver.objects.get_or_create(driver_id=driver_id, defaults={
            'user': user
        })

    # 출발/도착 야드
    Yard.objects.get_or_create(yard_id=departure_yard_id, defaults={
        'division_id': 1  # 기본 division ID를 수동으로 추가 (필요 시 수정)
    })
    Yard.objects.get_or_create(yard_id=arrival_yard_id, defaults={
        'division_id': 1
    })

print("CSV 데이터가 성공적으로 데이터베이스에 주입되었습니다.")
