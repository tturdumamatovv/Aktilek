# Generated by Django 5.0.7 on 2024-11-05 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0025_alter_category_name_alter_category_name_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='color',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='color',
            name='name_ky',
            field=models.CharField(max_length=50, null=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='color',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name='Цвет'),
        ),
    ]
