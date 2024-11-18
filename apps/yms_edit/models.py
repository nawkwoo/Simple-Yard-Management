from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# --- 공통 추상 모델 ---
class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

# --- Division ---
class Division(BaseModel):
    name = models.CharField(
        max_length=3,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{2,3}$", message="Division name must be 2-3 uppercase letters.")]
    )
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.full_name

    @classmethod
    def create_default_divisions(cls):
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
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="yards")
    yard_id = models.CharField(
        max_length=5,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{2}\d{2}$", message="Yard ID must follow format: 2 letters + 2 digits.")]
    )

    def __str__(self):
        return f"{self.division.name} - {self.yard_id}"

    def create_sites(self, equipment_types):
        for equipment_type in equipment_types:
            Site.objects.create(yard=self, equipment_type=equipment_type)

# --- Site ---
class Site(BaseModel):
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
        """장비 타입에 따라 수용 용량 자동 설정"""
        if not self.capacity:  # 수동으로 설정하지 않았을 때만 적용
            self.capacity = self.CAPACITY_MAPPING.get(self.equipment_type, 30)
        super().save(*args, **kwargs)

# --- Driver ---
class Driver(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"user_type": "staff"}
    )
    driver_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{6}\d{2}$", message="Driver ID must be 6 letters followed by 2 digits.")]
    )

    def __str__(self):
        return self.driver_id

# --- Truck ---
class Truck(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trucks")
    truck_id = models.CharField(max_length=4, unique=True, validators=[RegexValidator(regex=r"^\d{4}$", message="Truck ID must be 4 digits.")])
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='truck_images/', blank=True, null=True)

    def __str__(self):
        return self.truck_id

    def clean(self):
        if self.site.equipment_type != 'Truck':
            raise ValidationError("선택한 야드에 트럭 사이트가 없습니다.")

# --- Chassis ---
class Chassis(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="chassis")
    chassis_id = models.CharField(
        max_length=4, unique=True, validators=[RegexValidator(regex=r"^[A-Z]{4}$", message="Chassis ID must be 4 uppercase letters.")]
    )
    type = models.CharField(max_length=10, choices=[('Regular', 'Regular'), ('Light', 'Light'), ('Tandem', 'Tandem'), ('Tri Axle', 'Tri Axle')])
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='chassis_images/', blank=True, null=True)

    def __str__(self):
        return self.chassis_id

    def clean(self):
        if self.site.equipment_type != 'Chassis':
            raise ValidationError("선택한 야드에 샤시 사이트가 없습니다.")

# --- Container ---
class Container(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="containers")
    container_id = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{4}\d{7}$", message="Container ID must be 4 letters followed by 7 digits.")]
    )
    size = models.CharField(max_length=5, choices=[('40ST', '40ST'), ('40HC', '40HC'), ('20ST', '20ST'), ('45HC', '45HC')])
    type = models.CharField(
        max_length=10,
        choices=[('Dry', 'Dry'), ('Reefer', 'Reefer'), ('Flat Rack', 'Flat Rack'), ('ISO Tank', 'ISO Tank'), ('Open Top', 'Open Top'), ('Try Door', 'Try Door')]
    )
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='container_images/', blank=True, null=True)

    def __str__(self):
        return self.container_id

    def clean(self):
        if self.site.equipment_type != 'Container':
            raise ValidationError("선택한 야드에 컨테이너 사이트가 없습니다.")

# --- Trailer ---
class Trailer(BaseModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="trailers")
    trailer_id = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(regex=r"^[A-Z]{4}\d{6}$", message="Trailer ID must be 4 letters followed by 6 digits.")]
    )
    size = models.CharField(max_length=4, choices=[('53', '53'), ('48', '48')])
    serial_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='trailer_images/', blank=True, null=True)

    def __str__(self):
        return self.trailer_id

    def clean(self):
        if self.site.equipment_type != 'Trailer':
            raise ValidationError("선택한 야드에 트레일러 사이트가 없습니다.")