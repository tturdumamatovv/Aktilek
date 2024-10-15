from datetime import datetime
from decimal import Decimal

import requests
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import UserAddress, User
from apps.orders.models import Order, PromoCode
from apps.services.bonuces import calculate_bonus_points, apply_bonus_points
from apps.services.calculate_bonus import calculate_and_apply_bonus
from apps.services.generate_message import generate_order_message
from .serializers import (
    OrderSerializer,
    OrderPreviewSerializer,
    ReportSerializer,
    OrderListSerializer, PromoCodeSerializer, ReOrderSerializer
)

from apps.authentication.utils import (
    send_sms,
    generate_confirmation_code
)



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


class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Логика только для авторизованного пользователя
        if not request.user.is_anonymous:
            # Получаем данные о пользователе
            phone_number = request.user.phone_number
            full_name = request.user.full_name
            email = request.user.email

            # Проверяем самовывоз или доставка
            is_pickup = request.data.get('is_pickup', False)

            user_address = None
            if not is_pickup:
                # Проверяем, передан ли user_address_id
                user_address_id = request.data.get('user_address_id')
                if not user_address_id:
                    return Response({"error": "Address is required for delivery orders."},
                                    status=status.HTTP_400_BAD_REQUEST)

                try:
                    user_address = UserAddress.objects.get(id=user_address_id, user=request.user)
                except UserAddress.DoesNotExist:
                    return Response({"error": "Invalid address or address does not belong to user."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Создаем заказ для авторизованного пользователя без передачи phone_number, full_name, email
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(user=request.user)

            if not is_pickup and user_address:
                order.user_address = user_address
                order.save()

            order_serializer = OrderSerializer(order, context={'request': request})

            # Вставляем сообщение о доставке внутрь объекта заказа
            if not is_pickup:
                order_serializer.data['Доставка'] = "Уточните сумму доставки у оператора"

            return Response({
                "message": "Order created successfully.",
                "order": order_serializer.data
            }, status=status.HTTP_201_CREATED)

        # Если пользователь не авторизован
        return Response({"error": "Authentication is required to create an order."}, status=status.HTTP_401_UNAUTHORIZED)


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
