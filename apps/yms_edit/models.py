from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class BaseModel(models.Model):
    """공통 추상 모델"""
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간 추가

    class Meta:
        abstract = True


class Division(BaseModel):
    """디비전 모델"""
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

    @classmethod
    def create_default_divisions(cls):
        """기본 디비전 생성"""
        default_divisions = [
            {"name": "LA", "full_name": "Los Angeles"},
            {"name": "HOU", "full_name": "Houston"},
            {"name": "PHX", "full_name": "Phoenix"},
            {"name": "SAV", "full_name": "Savannah"},
            {"name": "MOB", "full_name": "Mobile"},
        ]
        for division in default_divisions:
            cls.objects.get_or_create(name=division["name"], defaults=division)


class Yard(BaseModel):
    """야드 모델"""
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
    """사이트 모델"""
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
        """장비 수용량 검증"""
        related_equipment = getattr(self, f"{self.equipment_type.lower()}s", None)
        if related_equipment and related_equipment.count() > self.capacity:
            raise ValidationError(f"{self.equipment_type} count exceeds capacity.")

    def save(self, *args, **kwargs):
        """자동 용량 설정"""
        self.capacity = self.CAPACITY_MAPPING.get(self.equipment_type, self.capacity)
        super().save(*args, **kwargs)


class Driver(BaseModel):
    """드라이버 모델"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"user_type": "staff"}
    )
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
    """트럭 모델"""
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
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='truck_images/', blank=True, null=True)  # 이미지 필드 추가

    def __str__(self):
        return self.truck_id


class Chassis(BaseModel):
    """샤시 모델"""
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
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='chassis_images/', blank=True, null=True)  # 이미지 필드 추가

    def __str__(self):
        return self.chassis_id


class Container(BaseModel):
    """컨테이너 모델"""
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
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='container_images/', blank=True, null=True)  # 이미지 필드 추가

    def __str__(self):
        return self.container_id


class Trailer(BaseModel):
    """트레일러 모델"""
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
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='trailer_images/', blank=True, null=True)  # 이미지 필드 추가

    def __str__(self):
        return self.trailer_id