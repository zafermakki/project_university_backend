# Generated by Django 4.2 on 2024-07-28 11:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0008_product_quantity"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="quantity",
        ),
    ]
