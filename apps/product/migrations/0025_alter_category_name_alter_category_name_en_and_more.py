# Generated by Django 5.0.7 on 2024-10-30 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0024_alter_productsize_bonus_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name_en',
            field=models.CharField(max_length=50, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name_ky',
            field=models.CharField(max_length=50, null=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name='Название'),
        ),
    ]
