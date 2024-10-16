# Generated by Django 5.0.7 on 2024-10-16 05:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_productinventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinventory',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='color_inventories', to='product.color', verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='productinventory',
            name='product_size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='product.productsize', verbose_name='Продукт'),
        ),
        migrations.AlterField(
            model_name='productinventory',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='size_inventories', to='product.size', verbose_name='Размер'),
        ),
    ]
