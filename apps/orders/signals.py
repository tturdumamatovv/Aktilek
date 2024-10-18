from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings

from apps.services.bonuces import apply_bonus_points
from apps.services.firebase_notification import send_firebase_notification
from apps.services.get_coordinates import get_coordinates
from .models import Order

from decouple import config

api_key=config('API_KEY')

def get_readable_order_status(status):
    if status == 'pending':
        return 'В ожидании'
    elif status == 'in_progress':
        return 'В процессе'
    elif status == 'delivery':
        return 'Доставка'
    elif status == 'completed':
        return 'Завершено'
    elif status == 'cancelled':
        return 'Отменено'
    else:
        return 'Неизвестный статус'


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    if instance.order_status == 'completed':
        instance.apply_bonuses()


@receiver(pre_save, sender=Order)
def check_status_change(sender, instance, **kwargs):
    if instance.pk:
        old_order = sender.objects.get(pk=instance.pk)
        # if old_order.order_status != instance.order_status and instance.order_status == 'completed':
        #     instance.delivery.delivery_time = datetime.now()
        #     instance.delivery.save()
        #     instance.user.last_order = datetime.now()
        #     instance.user.save()
        #     apply_bonus_points(instance.user, instance.total_bonus_amount)

        if instance.user and instance.user.fcm_token:
            readable_status = get_readable_order_status(instance.order_status)

            data = {
                "order_id": str(instance.id),
                "status": str(readable_status),
                "date": str(datetime.now().strftime("%d/%m/%Y, %H:%M:%S")),
                "type": "notificationPage"

            }
            print(data)
            try:
                send_firebase_notification(instance.user.fcm_token,
                                           "Изменение статуса заказа",
                                           f"Статус вашего заказа {instance.id} изменен на {instance.order_status}",
                                           data=data)
            except Exception as e:
                print(f"Ошибка при отправке уведомления: {e}")


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders_notifications", {
            "type": "send_notification",
            "message": f"Новый заказ №: {instance.id}"
        }
    )
