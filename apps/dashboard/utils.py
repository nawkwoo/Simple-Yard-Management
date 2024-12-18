# apps/dashboard/utils.py

import csv
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from apps.yms_edit.models import Yard, YardInventory
from .models import Movement


def process_csv(file_path):
    """
    주어진 CSV 파일을 처리하여 Movement 인스턴스를 생성합니다.

    CSV 파일 형식:
    equipment_type, equipment_id, departure_yard, arrival_yard, departure_time, arrival_time

    Args:
        file_path (str): CSV 파일의 경로.

    Raises:
        ValueError: 필수 필드가 누락되었거나 데이터 형식이 올바르지 않을 경우.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        with transaction.atomic():
            for row in reader:
                try:
                    # 필수 필드 검증
                    required_fields = ['equipment_type', 'equipment_id', 'departure_yard', 'arrival_yard', 'departure_time', 'arrival_time']
                    for field in required_fields:
                        if not row.get(field):
                            raise ValueError(f"필수 필드 '{field}'가 누락되었습니다.")

                    equipment_type = row['equipment_type']
                    equipment_id = row['equipment_id']
                    
                    # 야드 가져오기
                    departure_yard = Yard.objects.get(name=row['departure_yard'])
                    arrival_yard = Yard.objects.get(name=row['arrival_yard'])
                    
                    # 시간 파싱
                    departure_time = datetime.strptime(row['departure_time'], '%Y-%m-%d %H:%M:%S')
                    arrival_time = datetime.strptime(row['arrival_time'], '%Y-%m-%d %H:%M:%S')

                    # Movement 생성
                    Movement.objects.create(
                        equipment_type=equipment_type,
                        equipment_id=equipment_id,
                        departure_yard=departure_yard,
                        arrival_yard=arrival_yard,
                        departure_time=departure_time,
                        estimated_arrival_time=arrival_time
                    )
                except ObjectDoesNotExist as e:
                    # 야드가 존재하지 않을 경우 예외 처리
                    raise ValueError(f"야드 정보 오류: {e}")
                except ValueError as ve:
                    # 데이터 형식 오류
                    raise ValueError(f"데이터 형식 오류: {ve}")
