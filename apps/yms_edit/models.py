# apps/yms_edit/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from apps.accounts.models import Driver  # accounts.Driver를 임포트

# --- 공통 추상 모델 ---
class BaseModel(models.Model):
    """공통 추상 모델"""
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

# --- Division ---
class Division(BaseModel):
    """디비전 모델"""
    name = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{2,3}$",
            message="Division name must be 2-3 uppercase letters."
        )]
    )
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name

    @classmethod
    def create_default_divisions(cls):
        """기본 디비전 데이터 생성"""
        default_divisions = [
            {"name": "LA", "full_name": "Los Angeles"},
            {"name": "HOU", "full_name": "Houston"},
            {"name": "PHX", "full_name": "Phoenix"},
            {"name": "SAV", "full_name": "Savannah"},
            {"name": "MOB", "full_name": "Mobile"},
        ]
        for division in default_divisions:
            cls.objects.get_or_create(name=division["name"], defaults=division)

# --- Yard ---
class Yard(BaseModel):
    """야드 모델"""
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="yards")
    yard_id = models.CharField(
        max_length=5,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{2}\d{2}$",
            message="Yard ID must follow format: 2 letters + 2 digits."
        )]
    )
    address = models.CharField(max_length=255, null=True, blank=True)  # 주소 필드 추가
    latitude = models.FloatField(null=True, blank=True)  # 위도 필드
    longitude = models.FloatField(null=True, blank=True)  # 경도 필드

    def __str__(self):
        return f"{self.division.name} - {self.yard_id}"


# --- Yard Inventory ---
class YardInventory(models.Model):
    """야드 인벤토리 모델"""
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name="inventory")
    equipment_type = models.CharField(max_length=10)
    equipment_id = models.CharField(max_length=15, unique=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.equipment_type} - {self.equipment_id}"

# --- Site ---
class Site(BaseModel):
    """사이트 모델"""
    EQUIPMENT_TYPE_CHOICES = [
        ('Truck', 'Truck'),
        ('Chassis', 'Chassis'),
        ('Container', 'Container'),
        ('Trailer', 'Trailer')
    ]

    CAPACITY_MAPPING = {
        'Truck': 30,
        'Chassis': 20,
        'Container': 40,
        'Trailer': 10,
    }

    yard = models.ForeignKey(Yard, on_delete=models.CASCADE, related_name="sites")
    equipment_type = models.CharField(max_length=10, choices=EQUIPMENT_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.yard.yard_id} - {self.equipment_type} Site"

    def save(self, *args, **kwargs):
        """자동 수용 용량 설정"""
        if not self.capacity:
            self.capacity = self.CAPACITY_MAPPING.get(self.equipment_type, 30)
        super().save(*args, **kwargs)
    
    def is_full(self):
        """사이트가 최대 수용량에 도달했는지 확인"""
        current_count = Truck.objects.filter(site=self).count() + \
                        Chassis.objects.filter(site=self).count() + \
                        Container.objects.filter(site=self).count() + \
                        Trailer.objects.filter(site=self).count()
        return current_count >= self.capacity

# --- Equipment Models ---
class EquipmentBase(BaseModel):
    """공통 장비 모델"""
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        """장비 유효성 검사"""
        if self.site.is_full():
            raise ValidationError("해당 사이트는 이미 최대 수용량에 도달했습니다.")

class Truck(EquipmentBase):
    """트럭 모델"""
    transactions = GenericRelation('yms_view.Transaction')
    truck_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[RegexValidator(regex=r"^\d{4}$", message="Truck ID must be 4 digits.")]
    )

    def __str__(self):
        return self.truck_id

class Chassis(EquipmentBase):
    """샤시 모델"""
    transactions = GenericRelation('yms_view.Transaction')
    chassis_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{4}$", message="Chassis ID must be 4 uppercase letters.")]
    )
    type = models.CharField(
        max_length=10,
        choices=[('Regular', 'Regular'), ('Light', 'Light'), ('Tandem', 'Tandem'), ('Tri Axle', 'Tri Axle')]
    )

    def __str__(self):
        return self.chassis_id

class Container(EquipmentBase):
    """컨테이너 모델"""
    transactions = GenericRelation('yms_view.Transaction')
    container_id = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{4}\d{7}$", message="Container ID must be 4 letters followed by 7 digits.")]
    )
    size = models.CharField(max_length=5, choices=[
        ('40ST', '40ST'), ('40HC', '40HC'), ('20ST', '20ST'), ('45HC', '45HC')
    ])
    type = models.CharField(
        max_length=10,
        choices=[('Dry', 'Dry'), ('Reefer', 'Reefer'), ('Flat Rack', 'Flat Rack'),
                 ('ISO Tank', 'ISO Tank'), ('Open Top', 'Open Top'), ('Try Door', 'Try Door')]
    )

    def __str__(self):
        return self.container_id

class Trailer(EquipmentBase):
    """트레일러 모델"""
    transactions = GenericRelation('yms_view.Transaction')
    trailer_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{4}\d{6}$", message="Trailer ID must be 4 letters followed by 6 digits.")]
    )
    size = models.CharField(max_length=4, choices=[('53', '53'), ('48', '48')])

    def __str__(self):
        return self.trailer_id
