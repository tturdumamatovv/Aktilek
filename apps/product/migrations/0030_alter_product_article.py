# Generated by Django 5.0.7 on 2024-11-13 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0029_product_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='article',
            field=models.CharField(blank=True, max_length=9, verbose_name='Артикул'),
        ),
    ]
