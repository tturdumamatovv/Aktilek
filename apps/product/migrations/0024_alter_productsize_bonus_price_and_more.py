# Generated by Django 5.0.7 on 2024-10-24 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_productsize_bonus_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsize',
            name='bonus_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='Цена бонусами'),
        ),
        migrations.AlterField(
            model_name='productsize',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена'),
        ),
    ]
