# Generated by Django 5.0.7 on 2024-10-22 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_remove_sizechart_product_product_size_chart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sizechart',
            name='image',
            field=models.FileField(upload_to='size_charts/', verbose_name='Изображение'),
        ),
    ]
