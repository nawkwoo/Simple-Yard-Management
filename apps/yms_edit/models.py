from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Division(BaseModel):
    name = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2,3}$",
                message="Division name must be 2-3 uppercase letters."
            )
        ]
    )
    full_name = models.CharField(max_length=50)  # 예: "Los Angeles"

    def __str__(self):
        return self.full_name


class Yard(BaseModel):
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="yards")
    yard_id = models.CharField(
        max_length=5,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{2}\d{2}$",
                message="Yard ID must follow format: 2 letters + 2 digits (e.g., LA01)."
            )
        ]
    )

    def __str__(self):
        return f"{self.division.name} - {self.yard_id}"


class Site(BaseModel):
    EQUIPMENT_TYPE_CHOICES = [
        ('Truck', 'Truck'),
        ('Chassis', 'Chassis'),
        ('Container', 'Container'),
        ('Trailer', 'Trailer')
    ]
    CAPACITY_MAPPING = {
        "Truck": 30,
        "Chassis": 20,
        "Container": 40,
        "Trailer": 10,
    }

    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name="sites")
    equipment_type = models.CharField(max_length=10, choices=EQUIPMENT_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.yard.yard_id} - {self.equipment_type} Site"

    def clean(self):
        # Capacity 검증: 실제 장비 수가 용량을 초과하지 않도록 확인
        if self.equipment_type == 'Truck' and self.trucks.count() > self.capacity:
            raise ValidationError("Truck count exceeds capacity.")
        if self.equipment_type == 'Chassis' and self.chassis.count() > self.capacity:
            raise ValidationError("Chassis count exceeds capacity.")
        if self.equipment_type == 'Container' and self.containers.count() > self.capacity:
            raise ValidationError("Container count exceeds capacity.")
        if self.equipment_type == 'Trailer' and self.trailers.count() > self.capacity:
            raise ValidationError("Trailer count exceeds capacity.")

    def save(self, *args, **kwargs):
        # 자동 용량 설정
        self.capacity = self.CAPACITY_MAPPING.get(self.equipment_type, self.capacity)
        super().save(*args, **kwargs)


class Driver(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driver_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{6}\d{2}$",
                message="Driver ID must be 6 letters followed by 2 digits (e.g., ABCDEF01)."
            )
        ]
    )

    def __str__(self):
        return self.driver_id


class Truck(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trucks")
    truck_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}$",
                message="Truck ID must be exactly 4 digits."
            )
        ]
    )

    def __str__(self):
        return self.truck_id


class Chassis(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="chassis")
    chassis_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{4}$",
                message="Chassis ID must be exactly 4 uppercase letters."
            )
        ]
    )
    type = models.CharField(max_length=10, choices=[
        ('Regular', 'Regular'), ('Light', 'Light'),
        ('Tandem', 'Tandem'), ('Tri Axle', 'Tri Axle')
    ])

    def __str__(self):
        return self.chassis_id


class Container(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="containers")
    container_id = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{4}\d{7}$",
                message="Container ID must be 4 letters followed by 7 digits (e.g., ABCD1234567)."
            )
        ]
    )
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


class Trailer(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trailers")
    trailer_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{4}\d{6}$",
                message="Trailer ID must be 4 letters followed by 6 digits (e.g., ABCD123456)."
            )
        ]
    )
    size = models.CharField(max_length=4, choices=[
        ('53', '53'), ('48', '48')
    ])

    def __str__(self):
        return self.trailer_id