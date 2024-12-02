# apps/yms_edit/models.py

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from apps.accounts.models import Driver


# --- 공통 추상 모델 ---
class BaseModel(models.Model):
    """
    공통 추상 모델로, 모든 모델에 is_active와 created_at 필드를 추가합니다.
    """
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# --- Division ---
class Division(BaseModel):
    """
    디비전 모델로, 조직의 디비전을 나타냅니다.
    """
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
        """
        기본 디비전 데이터를 생성합니다.
        """
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
    """
    야드 모델로, 특정 디비전에 속한 야드를 나타냅니다.
    """
    division = models.ForeignKey(
        Division,
        on_delete=models.CASCADE,
        related_name="yards",
        help_text="야드가 속한 디비전"
    )
    yard_id = models.CharField(
        max_length=5,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{2}\d{2}$",
            message="Yard ID must follow format: 2 letters + 2 digits."
        )],
        help_text="예시: YD01 (야드 ID는 YD로 시작하고 두 자리 숫자로 구성됩니다.)"
    )

    def __str__(self):
        return f"{self.division.name} - {self.yard_id}"


# --- Yard Inventory ---
class YardInventory(models.Model):
    """
    야드 인벤토리 모델로, 특정 야드에 있는 장비의 재고를 나타냅니다.
    """
    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        related_name="inventory",
        help_text="장비가 속한 야드"
    )
    equipment_type = models.CharField(max_length=10, help_text="장비의 유형 (Truck, Chassis, etc.)")
    equipment_id = models.CharField(
        max_length=15,
        unique=True,
        help_text="장비의 고유 ID"
    )
    is_available = models.BooleanField(default=True, help_text="장비의 사용 가능 여부")

    def __str__(self):
        return f"{self.equipment_type} - {self.equipment_id}"


# --- Site ---
class Site(BaseModel):
    """
    사이트 모델로, 특정 야드 내에서 장비가 배치될 수 있는 장소를 나타냅니다.
    """
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

    yard = models.ForeignKey(
        Yard,
        on_delete=models.CASCADE,
        related_name="sites",
        help_text="사이트가 속한 야드"
    )
    equipment_type = models.CharField(
        max_length=10,
        choices=EQUIPMENT_TYPE_CHOICES,
        help_text="사이트에 배치할 장비의 유형"
    )
    capacity = models.PositiveIntegerField(
        help_text="사이트의 최대 수용 용량"
    )

    def __str__(self):
        return f"{self.yard.yard_id} - {self.equipment_type} Site"

    def save(self, *args, **kwargs):
        """
        저장 시, capacity가 설정되지 않은 경우 자동으로 설정합니다.
        """
        if not self.capacity:
            self.capacity = self.CAPACITY_MAPPING.get(self.equipment_type, 30)
        super().save(*args, **kwargs)

    def is_full(self):
        """
        사이트가 최대 수용 용량에 도달했는지 확인합니다.
        """
        current_count = (
            Truck.objects.filter(site=self).count() +
            Chassis.objects.filter(site=self).count() +
            Container.objects.filter(site=self).count() +
            Trailer.objects.filter(site=self).count()
        )
        return current_count >= self.capacity


# --- Equipment Models ---
class EquipmentBase(BaseModel):
    """
    공통 장비 모델로, 모든 장비에 공통으로 필요한 필드를 정의합니다.
    """
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        help_text="장비가 배치될 사이트"
    )
    serial_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="장비의 고유 일련번호"
    )
    image = models.ImageField(
        upload_to='equipment_images/',
        blank=True,
        null=True,
        help_text="장비의 이미지"
    )
    is_occupied = models.BooleanField(
        default=False,
        help_text="장비의 점유 여부"
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        장비가 배치될 사이트의 수용 용량을 확인합니다.
        """
        if self.site.is_full():
            raise ValidationError("해당 사이트는 이미 최대 수용량에 도달했습니다.")


class Truck(EquipmentBase):
    """
    트럭 모델
    """
    truck_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[RegexValidator(
            regex=r"^\d{4}$",
            message="Truck ID must be 4 digits."
        )],
        help_text="예시: 1234 (4자리 숫자)"
    )

    def __str__(self):
        return self.truck_id


class Chassis(EquipmentBase):
    """
    샤시 모델
    """
    chassis_id = models.CharField(
        max_length=4,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{4}$",
            message="Chassis ID must be 4 uppercase letters."
        )],
        help_text="예시: ABCD (4개의 대문자)"
    )
    type = models.CharField(
        max_length=10,
        choices=[('Regular', 'Regular'), ('Light', 'Light'), ('Tandem', 'Tandem'), ('Tri Axle', 'Tri Axle')],
        help_text="샤시의 유형"
    )

    def __str__(self):
        return self.chassis_id


class Container(EquipmentBase):
    """
    컨테이너 모델
    """
    container_id = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{4}\d{7}$",
            message="Container ID must be 4 letters followed by 7 digits."
        )],
        help_text="예시: ABCD1234567 (4개의 대문자 + 7개의 숫자)"
    )
    size = models.CharField(
        max_length=5,
        choices=[
            ('40ST', '40ST'),
            ('40HC', '40HC'),
            ('20ST', '20ST'),
            ('45HC', '45HC')
        ],
        help_text="컨테이너의 크기"
    )
    type = models.CharField(
        max_length=10,
        choices=[
            ('Dry', 'Dry'),
            ('Reefer', 'Reefer'),
            ('Flat Rack', 'Flat Rack'),
            ('ISO Tank', 'ISO Tank'),
            ('Open Top', 'Open Top'),
            ('Try Door', 'Try Door')
        ],
        help_text="컨테이너의 유형"
    )

    def __str__(self):
        return self.container_id


class Trailer(EquipmentBase):
    """
    트레일러 모델
    """
    trailer_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{4}\d{6}$",
            message="Trailer ID must be 4 letters followed by 6 digits."
        )],
        help_text="예시: ABCD123456 (4개의 대문자 + 6개의 숫자)"
    )
    size = models.CharField(
        max_length=4,
        choices=[
            ('53', '53'),
            ('48', '48')
        ],
        help_text="트레일러의 크기"
    )

    def __str__(self):
        return self.trailer_id
