# Generated by Django 4.2.6 on 2023-10-11 19:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Config",
            fields=[
                (
                    "key",
                    models.CharField(
                        max_length=100, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("value", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Team",
            fields=[
                (
                    "team_number",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("balance", models.BigIntegerField()),
            ],
        ),
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
                ("amount", models.BigIntegerField()),
                ("balance", models.BigIntegerField()),
                ("description", models.TextField()),
                ("is_for_interest", models.BooleanField()),
                ("recorded_at", models.IntegerField()),
                (
                    "recorded_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="transaction.team",
                    ),
                ),
            ],
        ),
    ]
