# Generated by Django 4.2.16 on 2024-11-20 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
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
                ("truck", models.CharField(blank=True, max_length=10, null=True)),
                ("chassis", models.CharField(blank=True, max_length=10, null=True)),
                ("container", models.CharField(blank=True, max_length=15, null=True)),
                ("trailer", models.CharField(blank=True, max_length=15, null=True)),
                ("departure_time", models.DateTimeField()),
                ("arrival_time", models.DateTimeField()),
                (
                    "arrival_yard",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders_arrived",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "departure_yard",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders_departed",
                        to="yms_edit.yard",
                    ),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="yms_edit.driver",
                    ),
                ),
            ],
        ),
    ]
