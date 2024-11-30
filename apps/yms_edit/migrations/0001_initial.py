# Generated by Django 4.2.16 on 2024-11-29 11:42

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Division",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "name",
                    models.CharField(
                        max_length=3,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Division name must be 2-3 uppercase letters.",
                                regex="^[A-Z]{2,3}$",
                            )
                        ],
                    ),
                ),
                ("full_name", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Site",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "equipment_type",
                    models.CharField(
                        choices=[
                            ("Truck", "Truck"),
                            ("Chassis", "Chassis"),
                            ("Container", "Container"),
                            ("Trailer", "Trailer"),
                        ],
                        max_length=10,
                    ),
                ),
                ("capacity", models.PositiveIntegerField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Yard",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "yard_id",
                    models.CharField(
                        max_length=5,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Yard ID must follow format: 2 letters + 2 digits.",
                                regex="^[A-Z]{2}\\d{2}$",
                            )
                        ],
                    ),
                ),
                (
                    "division",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="yards",
                        to="yms_edit.division",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="YardInventory",
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
                ("equipment_type", models.CharField(max_length=10)),
                ("equipment_id", models.CharField(max_length=15, unique=True)),
                ("is_available", models.BooleanField(default=True)),
                (
                    "yard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inventory",
                        to="yms_edit.yard",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Truck",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("serial_number", models.CharField(max_length=15, unique=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="equipment_images/"
                    ),
                ),
                (
                    "truck_id",
                    models.CharField(
                        max_length=4,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Truck ID must be 4 digits.", regex="^\\d{4}$"
                            )
                        ],
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="yms_edit.site"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Trailer",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("serial_number", models.CharField(max_length=15, unique=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="equipment_images/"
                    ),
                ),
                (
                    "trailer_id",
                    models.CharField(
                        max_length=10,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Trailer ID must be 4 letters followed by 6 digits.",
                                regex="^[A-Z]{4}\\d{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "size",
                    models.CharField(
                        choices=[("53", "53"), ("48", "48")], max_length=4
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="yms_edit.site"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="site",
            name="yard",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sites",
                to="yms_edit.yard",
            ),
        ),
        migrations.CreateModel(
            name="Container",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("serial_number", models.CharField(max_length=15, unique=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="equipment_images/"
                    ),
                ),
                (
                    "container_id",
                    models.CharField(
                        max_length=11,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Container ID must be 4 letters followed by 7 digits.",
                                regex="^[A-Z]{4}\\d{7}$",
                            )
                        ],
                    ),
                ),
                (
                    "size",
                    models.CharField(
                        choices=[
                            ("40ST", "40ST"),
                            ("40HC", "40HC"),
                            ("20ST", "20ST"),
                            ("45HC", "45HC"),
                        ],
                        max_length=5,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("Dry", "Dry"),
                            ("Reefer", "Reefer"),
                            ("Flat Rack", "Flat Rack"),
                            ("ISO Tank", "ISO Tank"),
                            ("Open Top", "Open Top"),
                            ("Try Door", "Try Door"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="yms_edit.site"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Chassis",
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
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("serial_number", models.CharField(max_length=15, unique=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="equipment_images/"
                    ),
                ),
                (
                    "chassis_id",
                    models.CharField(
                        max_length=4,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Chassis ID must be 4 uppercase letters.",
                                regex="^[A-Z]{4}$",
                            )
                        ],
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("Regular", "Regular"),
                            ("Light", "Light"),
                            ("Tandem", "Tandem"),
                            ("Tri Axle", "Tri Axle"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="yms_edit.site"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
