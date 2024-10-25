import requests

import xml.etree.ElementTree as ET
from datetime import datetime
from decouple import config

from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import localtime

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import UserAddress
from apps.orders.models import Order, PromoCode, Warehouse
from .serializers import (
    OrderSerializer,
    OrderPreviewSerializer,
    ReportSerializer,
    OrderListSerializer, PromoCodeSerializer, ReOrderSerializer
)
from ..freedompay import generate_signature
from ...services.bonuces import calculate_bonus_points, apply_bonus_points

PAYBOX_URL = config('PAYBOX_URL')
PAYBOX_MERCHANT_ID = config('PAYBOX_MERCHANT_ID')
PAYBOX_MERCHANT_SECRET = config('PAYBOX_MERCHANT_SECRET')
PAYBOX_MERCHANT_SECRET_PAYOUT = config('PAYBOX_MERCHANT_SECRET_PAYOUT')

class ListOrderView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return Order.objects.none()
        return Order.objects.filter(user=user).order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request
        })
        return context


def get_user_orders(request):
    user_id = request.GET.get('user_id')
    orders = Order.objects.filter(user_id=user_id).values(
        'id', 'order_time', 'total_amount', 'order_status'
    ).order_by('-id')
    for order in orders:
        order['order_time'] = localtime(order['order_time']).strftime('%d/%m/%Y, %H:%M')
        order['order_status'] = dict(Order._meta.get_field('order_status').choices)[order['order_status']]

    return JsonResponse({'orders': list(orders)}, safe=False)


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            # Сохраняем основные данные
            is_pickup = request.data.get('is_pickup', False)
            user_address = None
            warehouse = None

            if is_pickup:
                warehouse_id = request.data.get('warehouse_id')
                if not warehouse_id:
                    return Response({"error": "ID склада обязателен для самовывоза."},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    warehouse = Warehouse.objects.get(id=warehouse_id)
                except Warehouse.DoesNotExist:
                    return Response({"error": "Некорректный склад или склад не найден."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Handle non-pickup orders requiring a user address
                user_address_id = request.data.get('user_address_id')
                if not user_address_id:
                    return Response({"error": "Адрес обязателен для курьерских заказов."},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    user_address = UserAddress.objects.get(id=user_address_id, user=request.user)
                except UserAddress.DoesNotExist:
                    return Response({"error": "Некорректный адрес или адрес не принадлежит пользователю."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Create order and process items
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(user=request.user)

            # Attach warehouse or address to the order
            if is_pickup:
                order.warehouse = warehouse
            elif user_address:
                order.user_address = user_address
            order.save()

            # Уменьшаем количество продуктов на складе и рассчитываем стоимость заказа
            total_order_amount = 0
            total_bonus_amount = 0  # Инициализируем сумму бонусов
            for item in order.order_items.all():
                product_size = item.product_size
                if product_size.quantity >= item.quantity:
                    product_size.quantity -= item.quantity
                    product_size.save()
                    item.is_ordered = True
                    item.save()

                    # Рассчитываем цену на основе скидок и бонусов
                    if item.is_bonus and product_size.bonus_price is not None:
                        item_price = product_size.bonus_price
                        total_bonus_amount += item_price * item.quantity
                    elif product_size.discounted_price is not None:
                        item_price = product_size.discounted_price
                    else:
                        item_price = product_size.price

                    # Добавляем стоимость каждого товара в итоговую сумму заказа
                    total_order_amount += item_price * item.quantity

                else:
                    return Response({"error": f"Недостаточно товара на складе для {item.product_size.product.name}."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Обрабатываем оплату бонусами
            if total_bonus_amount > 0:
                if request.user.bonus is None or request.user.bonus < total_bonus_amount:
                    return Response({"error": "Недостаточно бонусов для оплаты."}, status=status.HTTP_400_BAD_REQUEST)

                request.user.bonus -= total_bonus_amount
                request.user.save()

            # Обновляем итоговую сумму заказа
            order.total_amount = total_order_amount
            order.save()

            # Формируем ответ на заказ
            order_serializer = OrderSerializer(order, context={'request': request})

            response_data = {
                "message": "Заказ успешно создан.",
                "order": order_serializer.data
            }

            # Убедитесь, что тип оплаты - карта
            payment_method = request.data.get('payment_method', 'cash')
            if payment_method == 'card':
                email = request.user.email
                phone_number = request.user.phone_number  # Убедитесь, что номер телефона существует
                payment_url = self.create_freedompay_payment(order, email, phone_number)

                if isinstance(payment_url, Response):
                    # Вернем ошибку, если произошел сбой при инициализации платежа
                    return payment_url

                # Добавляем redirect_url в ответ
                response_data["redirect_url"] = payment_url

            # Отправляем подтверждение по email, если указано
            email = request.user.email
            if email:
                self.send_order_confirmation_email(email, order_serializer.data)

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response({"error": "Требуется аутентификация для создания заказа."}, status=status.HTTP_401_UNAUTHORIZED)

    def create_freedompay_payment(self, order, email, phone_number):
        url = f"{PAYBOX_URL}/init_payment.php"
        amount = order.total_amount
        order_id = order.id
        params = {
            'pg_merchant_id': PAYBOX_MERCHANT_ID,
            'pg_order_id': order_id,
            'pg_amount': amount,
            'pg_currency': 'KGS',
            'pg_description': f"Оплата заказа #{order_id}",
            'pg_user_phone': phone_number,
            'pg_user_contact_email': email,
            'pg_result_url': 'https://ak-tilek.kg/ru/',
            'pg_success_url': 'https://ak-tilek.kg/ru/success/',
            'pg_failure_url': 'https://ak-tilek.kg/ru/failure/',
            'pg_testing_mode': 1,
            'pg_salt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

        # Генерация подписи
        params['pg_sig'] = generate_signature(params, 'init_payment.php')

        try:
            response = requests.post(url, data=params)
            response.raise_for_status()  # Raise an error for bad responses

            # Log the response for debugging
            print("Response from payment gateway:", response.text)

            # Join response text if it's split into multiple parts
            response_text = ''.join(response.text)  # Concatenate if it's broken into parts

            # Parse the XML response
            root = ET.fromstring(response_text)
            payment_url = root.find('pg_redirect_url')

            if payment_url is None or not payment_url.text:
                raise ValueError("Payment URL is missing in the response.")

            # Return the payment URL as a clean string
            return payment_url.text

        except ET.ParseError:
            return Response({"error": "Failed to parse payment gateway response."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.RequestException as e:
            print(f"Error during request to Paybox: {e}")
            return Response({"error": "Failed to initiate payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_order_confirmation_email(self, email, order_data):
        subject = 'Ваш заказ успешно создан'
        html_message = render_to_string('order_confirmation_email.html', {'order': order_data})
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message
        )


class OrderPreviewView(generics.GenericAPIView):
    serializer_class = OrderPreviewSerializer

    def post(self, request, *args, **kwargs):
        return Response({"message": "Order preview logic is simplified."}, status=status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def create(self, request, *args, **kwargs):
        report, serializer = self.create_report(request)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create_report(self, request):
        description = request.data.get('description')
        contact_number = request.data.get('contact_number')
        image = request.FILES.get('image') if 'image' in request.FILES else None
        report_data = {
            'description': description,
            'contact_number': contact_number,
            'image': image
        }
        serializer = self.get_serializer(data=report_data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        return report, serializer


class PromoCodeDetailView(APIView):
    def get(self, request, code):
        try:
            promo_code = PromoCode.objects.get(code=code)
            if promo_code.is_valid():
                serializer = PromoCodeSerializer(promo_code)
                return Response(serializer.data)
            else:
                return Response({"error": "Промокод не активен или срок его действия истек"},
                                status=status.HTTP_404_NOT_FOUND)
        except PromoCode.DoesNotExist:
            return Response({"error": "Промокод не найден"}, status=status.HTTP_404_NOT_FOUND)


class CreateReOrderView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            serializer = ReOrderSerializer(order, context={'request': request})
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            # Проверяем, принадлежит ли заказ текущему пользователю
            if order.user != request.user:
                return Response({'error': 'Вы не можете повторно заказать этот заказ.'},
                                status=status.HTTP_403_FORBIDDEN)

            if not order.is_pickup and order.user_address:
                user_address_id = order.user_address.id
            else:
                user_address_id = None

            order_data = {
                'is_pickup': order.is_pickup,
                'payment_method': order.payment_method,
                'comment': order.comment,
                'user_address_id': user_address_id,
                'products': [{
                    'product_size_id': item.product_size.id,
                    'quantity': item.quantity,
                    'color_id': item.color_id,
                    'size_id': item.size_id,
                    'is_bonus': item.is_bonus
                } for item in order.order_items.all()]
            }

            # Создаем новый заказ
            serializer = OrderSerializer(data=order_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            new_order = serializer.save(user=request.user)

            return Response({
                "message": "Order created successfully.",
                "order": OrderSerializer(new_order, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
