# Generated by Django 5.2.3 on 2025-07-09 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_auto_20250709_0341"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="price_at_order",
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
