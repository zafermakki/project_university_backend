# Generated by Django 4.2 on 2025-05-12 19:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cart", "0010_remove_purchase_latitude_remove_purchase_longitude"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchase",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="purchase",
            name="country",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="purchase",
            name="phone",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
