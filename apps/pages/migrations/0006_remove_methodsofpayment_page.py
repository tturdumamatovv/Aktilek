# Generated by Django 5.0.7 on 2024-10-18 04:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_alter_banner_image_desktop_alter_banner_image_mobile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='methodsofpayment',
            name='page',
        ),
    ]
