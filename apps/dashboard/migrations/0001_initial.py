# Generated by Django 4.2.17 on 2024-12-17 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("yms_edit", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("COMPLETED", "Completed"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        help_text="이동 상태",
                        max_length=10,
                    ),
                ),
                (
                    "status_move",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("DEPARTURED", "Departured"),
                            ("ARRIVED", "Arrived"),
                        ],
                        default="PENDING",
                        help_text="주문의 상태",
                        max_length=10,
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True,
                        help_text="주문 처리 중 발생한 에러 메시지",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, help_text="주문 생성 시간"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, help_text="주문 수정 시간"),
                ),
                ("departure_time", models.DateTimeField(help_text="출발 시간")),
                ("arrival_time", models.DateTimeField(help_text="도착시간 시간")),
                (
                    "arrival_yard",
                    models.ForeignKey(
                        help_text="도착 야드",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="arrival_orders",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "chassis",
                    models.ForeignKey(
                        blank=True,
                        help_text="사용할 샤시",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="yms_edit.chassis",
                    ),
                ),
                (
                    "container",
                    models.ForeignKey(
                        blank=True,
                        help_text="사용할 컨테이너",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="yms_edit.container",
                    ),
                ),
                (
                    "departure_yard",
                    models.ForeignKey(
                        help_text="출발 야드",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="departure_orders",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        help_text="주문을 처리할 운전자",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="accounts.driver",
                    ),
                ),
                (
                    "trailer",
                    models.ForeignKey(
                        blank=True,
                        help_text="사용할 트레일러",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="yms_edit.trailer",
                    ),
                ),
                (
                    "truck",
                    models.ForeignKey(
                        blank=True,
                        help_text="사용할 트럭",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="yms_edit.truck",
                    ),
                ),
            ],
            options={
                "verbose_name": "주문",
                "verbose_name_plural": "주문들",
                "ordering": ["-created_at"],
            },
        ),
    ]
