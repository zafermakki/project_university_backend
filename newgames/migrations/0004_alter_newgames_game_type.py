# Generated by Django 4.2 on 2024-11-26 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0015_category_description"),
        ("newgames", "0003_newgames_game_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newgames",
            name="game_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"parent_category__name": "Games"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="new_games",
                to="products.subcategory",
            ),
        ),
    ]