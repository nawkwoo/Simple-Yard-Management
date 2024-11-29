# from django.test import TestCase
# from django.core.files.uploadedfile import SimpleUploadedFile
# from apps.yms_edit.models import Division, Yard, Site, Truck, Chassis, Container, Trailer
# from apps.dashboard.models import Order
# from apps.accounts.models import CustomUser

# class DashboardTestCase(TestCase):
#     def setUp(self):
#         """테스트 데이터 초기화"""
#         # 사용자 생성
#         self.admin_user = CustomUser.objects.create_user(
#             username="admin", password="password123", user_type="admin"
#         )
#         self.driver_user = CustomUser.objects.create_user(
#             username="driver1", password="password123", user_type="staff"
#         )

#         # 디비전 생성
#         self.division = Division.objects.create(name="LA", full_name="Los Angeles Division")

#         # 야드 생성
#         self.yard1 = Yard.objects.create(division=self.division, yard_id="LA01")
#         self.yard2 = Yard.objects.create(division=self.division, yard_id="LA02")

#         # 사이트 생성
#         self.site1 = Site.objects.create(yard=self.yard1, equipment_type="Truck", capacity=10)
#         self.site2 = Site.objects.create(yard=self.yard2, equipment_type="Truck", capacity=10)

#         # 장비 생성 (트럭)
#         self.truck1 = Truck.objects.create(site=self.site1, serial_number="T123", truck_id="1234")
#         self.truck2 = Truck.objects.create(site=self.site2, serial_number="T124", truck_id="1235")

#         # 장비 생성 (샤시)
#         self.chassis1 = Chassis.objects.create(site=self.site1, serial_number="C123", chassis_id="CH01")
#         self.chassis2 = Chassis.objects.create(site=self.site2, serial_number="C124", chassis_id="CH02")

#     def test_csv_upload_and_order_creation(self):
#         """CSV 파일 업로드로 주문 생성 테스트"""
#         # CSV 파일 내용
#         csv_content = """트럭,샤시,컨테이너,트레일러,운전자,출발시간,도착시간,출발위치,도착위치
# T123,C123,,,driver1,2024-11-21 09:00,2024-11-21 15:00,LA01,LA02
# T124,C124,,,driver1,2024-11-21 10:00,2024-11-21 16:00,LA02,LA01
# """
#         # CSV 파일 업로드
#         csv_file = SimpleUploadedFile("orders.csv", csv_content.encode("utf-8"), content_type="text/csv")
#         response = self.client.post("/dashboard/upload/", {"csv_file": csv_file})

#         # 주문이 생성되었는지 확인
#         self.assertEqual(Order.objects.count(), 2)
#         order1 = Order.objects.first()

#         # 주문 데이터 확인
#         self.assertEqual(order1.truck.serial_number, "T123")
#         self.assertEqual(order1.chassis.serial_number, "C123")
#         self.assertEqual(order1.departure_yard, self.yard1)
#         self.assertEqual(order1.arrival_yard, self.yard2)