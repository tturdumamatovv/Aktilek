# your_app/templatetags/chat_tags.py

from django import template

from apps.orders.models import Order

register = template.Library()


@register.simple_tag
def get_user_orders(user):
    return Order.objects.filter(user=user)
