from django.db import models
from django.conf import settings

class Division(models.Model):
    DIVISION_CHOICES = [
        ('LA', 'Los Angeles'),
        ('PHX', 'Phoenix'),
        ('HOU', 'Houston'),
        ('SAV', 'Savannah'),
        ('MOB', 'Mobile'),
    ]
    name = models.CharField(max_length=3, choices=DIVISION_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_display()

class Yard(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="yards")
    yard_id = models.CharField(max_length=5, unique=True)  # Division + 2자리 숫자

    def __str__(self):
        return f"{self.division.name} - {self.yard_id}"

class Site(models.Model):
    EQUIPMENT_TYPE_CHOICES = [
        ('Truck', 'Truck'),
        ('Chassis', 'Chassis'),
        ('Container', 'Container'),
        ('Trailer', 'Trailer')
    ]
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name="sites")
    equipment_type = models.CharField(max_length=10, choices=EQUIPMENT_TYPE_CHOICES)  # 장비 종류 선택
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.yard.yard_id} - {self.equipment_type} Site"

    def save(self, *args, **kwargs):
        if self.equipment_type == 'Truck':
            self.capacity = 30
        elif self.equipment_type == 'Chassis':
            self.capacity = 20
        elif self.equipment_type == 'Container':
            self.capacity = 40
        elif self.equipment_type == 'Trailer':
            self.capacity = 10
        super().save(*args, **kwargs)

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver_id = models.CharField(max_length=8, unique=True)  # 6 Letters + 2 Digits

    def __str__(self):
        return self.driver_id

class Truck(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trucks")
    truck_id = models.CharField(max_length=4, unique=True)  # 4자리 ID

    def __str__(self):
        return self.truck_id

class Chassis(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="chassis")
    chassis_id = models.CharField(max_length=4, unique=True)  # 4 Letters
    type = models.CharField(max_length=10, choices=[
        ('Regular', 'Regular'), ('Light', 'Light'), 
        ('Tandem', 'Tandem'), ('Tri Axle', 'Tri Axle')
    ])

    def __str__(self):
        return self.chassis_id

class Container(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="containers")
    container_id = models.CharField(max_length=11, unique=True)  # 4 Letters + 7 Digits
    size = models.CharField(max_length=5, choices=[
        ('40ST', '40ST'), ('40HC', '40HC'), 
        ('20ST', '20ST'), ('45HC', '45HC')
    ])
    type = models.CharField(max_length=10, choices=[
        ('Dry', 'Dry'), ('Reefer', 'Reefer'), 
        ('Flat Rack', 'Flat Rack'), ('ISO Tank', 'ISO Tank'), 
        ('Open Top', 'Open Top'), ('Try Door', 'Try Door')
    ])

    def __str__(self):
        return self.container_id

class Trailer(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trailers")
    trailer_id = models.CharField(max_length=10, unique=True)  # 4 Letters + 6 Digits
    size = models.CharField(max_length=4, choices=[
        ('53', '53'), ('48', '48')
    ])

    def __str__(self):
        return self.trailer_id