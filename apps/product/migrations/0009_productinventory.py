# Generated by Django 5.0.7 on 2024-10-16 05:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0008_category_is_promoted'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='Количество')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='color_inventories', to='product.color')),
                ('product_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='product.productsize')),
                ('size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='size_inventories', to='product.size')),
            ],
            options={
                'verbose_name': 'Запас продукта',
                'verbose_name_plural': 'Запасы продуктов',
                'unique_together': {('product_size', 'size', 'color')},
            },
        ),
    ]
