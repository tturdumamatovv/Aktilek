# Generated by Django 5.0.7 on 2024-10-23 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_ordered',
            field=models.BooleanField(default=False, verbose_name='Заказан'),
        ),
    ]
