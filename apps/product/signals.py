from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.translation import gettext_lazy as _

from apps.product.models import Product


@receiver(post_save, sender=Product)
def validate_product_images(sender, instance, **kwargs):
    color_images = {}

    for image in instance.product_images.all():
        color = image.color
        if color:
            if color in color_images:
                color_images[color].append(image)
            else:
                color_images[color] = [image]

    missing_images = []
    for product_size in instance.product_sizes.all():
        color = product_size.color
        if color not in color_images:
            missing_images.append(color.name)

    if missing_images:
        # Сообщение об ошибке, которое будет отображено в админке
        form.add_error(
            None,
            ValidationError(
                _("Для следующих цветов должны быть загружены хотя бы одно изображение: %(colors)s."),
                params={'colors': ', '.join(missing_images)}
            )
        )
