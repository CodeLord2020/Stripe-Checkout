# Generated by Django 4.1.7 on 2023-07-19 12:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products1", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentHistory",
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
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "payment_status",
                    models.CharField(
                        choices=[("P", "pending"), ("C", "completed"), ("F", "failed")],
                        default="P",
                        max_length=1,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products1.product",
                    ),
                ),
            ],
        ),
    ]
