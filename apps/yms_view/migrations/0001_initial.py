# Generated by Django 4.2.16 on 2024-12-02 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("yms_edit", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "equipment_type",
                    models.CharField(
                        choices=[
                            ("Truck", "Truck"),
                            ("Chassis", "Chassis"),
                            ("Container", "Container"),
                            ("Trailer", "Trailer"),
                            ("PersonalVehicle", "Personal Vehicle"),
                        ],
                        help_text="장비 유형",
                        max_length=20,
                    ),
                ),
                (
                    "movement_time",
                    models.DateTimeField(auto_now_add=True, help_text="이동 시간"),
                ),
                (
                    "details",
                    models.TextField(blank=True, help_text="추가적인 정보", null=True),
                ),
                (
                    "arrival_yard",
                    models.ForeignKey(
                        help_text="도착 야드",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions_arrived",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "chassis",
                    models.ForeignKey(
                        blank=True,
                        help_text="샤시",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="yms_edit.chassis",
                    ),
                ),
                (
                    "container",
                    models.ForeignKey(
                        blank=True,
                        help_text="컨테이너",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="yms_edit.container",
                    ),
                ),
                (
                    "departure_yard",
                    models.ForeignKey(
                        help_text="출발 야드",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions_departed",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "trailer",
                    models.ForeignKey(
                        blank=True,
                        help_text="트레일러",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="yms_edit.trailer",
                    ),
                ),
                (
                    "truck",
                    models.ForeignKey(
                        blank=True,
                        help_text="트럭",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transactions",
                        to="yms_edit.truck",
                    ),
                ),
            ],
        ),
    ]