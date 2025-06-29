# Generated by Django 4.2 on 2025-04-22 12:54

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_remove_user_permissions_alter_user_user_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                max_length=250,
                unique=True,
                validators=[django.contrib.auth.validators.UnicodeUsernameValidator],
            ),
        ),
    ]
