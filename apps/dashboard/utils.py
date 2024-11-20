import csv
from datetime import datetime
from django.db import transaction
from yms_edit.models import YardInventory
from .models import Movement

def process_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        with transaction.atomic():
            for row in reader:
                equipment_type = row['equipment_type']
                equipment_id = row['equipment_id']
                departure_yard = Yard.objects.get(name=row['departure_yard'])
                arrival_yard = Yard.objects.get(name=row['arrival_yard'])
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