# Generated by Django 5.0.7 on 2024-10-14 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_alter_orderitem_size_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='color_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Название цвета'),
        ),
    ]
