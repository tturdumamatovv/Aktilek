# Generated by Django 5.0.7 on 2024-10-23 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0020_alter_country_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_ordered',
        ),
    ]
