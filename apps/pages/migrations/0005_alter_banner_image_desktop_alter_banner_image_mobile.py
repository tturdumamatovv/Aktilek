# Generated by Django 5.0.7 on 2024-10-18 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_delete_deliverypayment_remove_methodsofpayment_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='image_desktop',
            field=models.ImageField(max_length=5000, upload_to='images/banners/desktop/%Y/%m/', verbose_name='Картинка круп'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image_mobile',
            field=models.ImageField(max_length=5000, upload_to='images/banners/mobile/%Y/%m/', verbose_name='Картинка моб'),
        ),
    ]
