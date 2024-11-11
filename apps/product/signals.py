from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from apps.product.models import Product, ProductImage


@receiver(post_save, sender=Product)
def validate_product_images(sender, instance, **kwargs):
    # Проверка наличия изображения для каждого варианта
    for product_size in instance.product_sizes.all():
        if not ProductImage.objects.filter(product=instance).exists():
            raise ValidationError("Для каждого варианта продукта должно быть загружено хотя бы одно изображение.")
