import pytz
from django.db import transaction
from django.conf import settings
from rest_framework import serializers
from apps.orders.models import (
    Order,
    OrderItem,
    Report,
    PromoCode, Warehouse
)
from apps.product.models import ProductSize, Product, Size, Topping, Color, ProductImage
from django.utils.translation import gettext_lazy as _


class ToppingSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Topping
        fields = ['id', 'name', 'price']


class ProductOrderItemSerializer(serializers.ModelSerializer):
    product_size_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(default=1)
    is_bonus = serializers.BooleanField(default=False)

    # Новый метод для получения информации о продукте
    product = serializers.SerializerMethodField(read_only=True)
    color = serializers.SerializerMethodField(read_only=True)
    size = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_size_id', 'quantity', 'is_bonus', 'product', 'color', 'size']

    def validate(self, data):
        product_size_id = data.get('product_size_id')

        product_size = ProductSize.objects.filter(id=product_size_id).first()
        if not product_size:
            raise serializers.ValidationError(f"ProductSize with id {product_size_id} does not exist.")

        return data

    def get_product(self, obj):
        product_size = obj.product_size  # Получаем ProductSize
        product = product_size.product
        request = self.context.get('request')  # Получаем контекст запроса
        image_url = product.photo.url if product.photo else None

        if request and image_url:
            image_url = request.build_absolute_uri(image_url)  # Строим полный URL

        return {
            'id': product.id,
            'name': product.name,
            'price': product.discounted_price if product.discounted_price else product.price,
            'image': image_url
        }

    def get_color(self, obj):
        color = obj.product_size.color
        return {
            'id': color.id,
            'name': color.name,
            'hex_code': color.hex_code,
        }

    def get_size(self, obj):
        size = obj.product_size.size
        return {
            'id': size.id,
            'name': size.name,
            'quantity': size.quantity
        }


class OrderListSerializer(serializers.ModelSerializer):
    order_items = ProductOrderItemSerializer(many=True, required=False)
    total_amount = serializers.SerializerMethodField()
    order_time = serializers.SerializerMethodField()
    user_address = serializers.SerializerMethodField()
    app_download_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'order_time', 'order_items', 'total_bonus_amount',
                  'is_pickup', 'user_address', 'app_download_url', 'order_status']

    def get_total_amount(self, obj):
        return obj.get_total_amount()

    def get_order_time(self, obj):
        local_tz = pytz.timezone(settings.TIME_ZONE)
        order_time = obj.order_time.astimezone(local_tz)
        return order_time.strftime('%Y-%m-%d %H:%M')

    def get_user_address(self, obj):
        if obj.is_pickup:
            return "Самовывоз"

        # Проверяем, связан ли заказ с пользователем и берем данные о номере телефона оттуда
        if obj.user:
            return obj.user.phone_number  # Информация о пользователе через ForeignKey

        # Иначе проверяем, был ли указан адрес (для неавторизованных пользователей)
        if obj.user_address:
            return f"{obj.user_address.city}, {obj.user_address.apartment_number}"

        return "Адрес не указан"

    def get_app_download_url(self, obj):
        return None  # Поле app_download_link было связано с моделью TelegramBotToken, которая была удалена


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderItemSerializer(many=True, source='order_items', required=True)
    order_source = serializers.ChoiceField(choices=[('web', 'web'), ('mobile', 'mobile')], default='web')
    change = serializers.IntegerField(default=0)
    is_pickup = serializers.BooleanField(default=False)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    user_address_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_info = serializers.SerializerMethodField()
    warehouse_city = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_time', 'total_amount', 'delivery_info', 'is_pickup', 'user_address_id', 'order_status',
            'products', 'payment_method', 'change', 'order_source', 'comment',
            'promo_code', 'warehouse_city',
        ]
        read_only_fields = ['total_amount', 'order_time', 'order_status']

    def get_delivery_info(self, obj):
        return "Уточните сумму доставки у оператора" if not obj.is_pickup else None

    def get_warehouse_city(self, obj):
        if obj.is_pickup:
            warehouse = Warehouse.objects.filter(is_primary=True).first()
            return warehouse.city if warehouse else "Склад не найден"
        return None

    def validate(self, data):
        if not data.get('is_pickup') and self.context['request'].user.is_authenticated:
            if not data.get('user_address_id'):
                raise serializers.ValidationError({"user_address_id": "Адрес пользователя обязателен для курьерской доставки."})
        return data

    def create(self, validated_data):
        products_data = validated_data.pop('order_items', [])
        promo_code_data = validated_data.pop('promo_code', None)
        user_address_id = validated_data.pop('user_address_id', None)  # Адрес для авторизованного

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            if user_address_id:
                order.user_address_id = user_address_id
                order.save()

            if promo_code_data:
                promo_code_instance = PromoCode.objects.filter(code=promo_code_data).first()
                if not promo_code_instance or not promo_code_instance.is_valid():
                    raise serializers.ValidationError({"promo_code": "Промокод недействителен или его срок истек."})
                order.promo_code = promo_code_instance
                order.save()

            # Добавляем продукты в заказ
            for product_data in products_data:
                product_size = ProductSize.objects.filter(id=product_data['product_size_id']).first()
                if not product_size:
                    raise serializers.ValidationError(f"ProductSize with id {product_data['product_size_id']} does not exist.")

                order_item = OrderItem(
                    order=order,
                    product_size=product_size,
                    quantity=product_data['quantity'],
                    is_bonus=product_data.get('is_bonus', False)
                )
                order_item.save()  # Сохраняем элемент заказа

                # Обновляем статус продукта
                product_size.product.is_ordered = True
                product_size.product.save()

        return order


class ProductOrderItemPreviewSerializer(serializers.Serializer):
    product_size_id = serializers.IntegerField(write_only=True)
    topping_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    quantity = serializers.IntegerField()


class OrderPreviewSerializer(serializers.Serializer):
    user_address_id = serializers.IntegerField()


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['image', 'description', 'contact_number']


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = ['code', 'valid_from', 'valid_to', 'type', 'discount', 'active']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ReOrderProductSizeSerializer(serializers.ModelSerializer):
    sizes = SizeSerializer(many=True, read_only=True)
    is_selected = serializers.SerializerMethodField()

    class Meta:
        model = ProductSize
        fields = ['id', 'sizes', 'is_selected']

    def get_is_selected(self, product_size):
        order_item = self.context.get('order_item')
        if order_item and order_item.product_size:
            return order_item.product_size == product_size
        return False


class ReOrderToppingSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    is_selected = serializers.SerializerMethodField()

    class Meta:
        model = Topping
        fields = ['id', 'name', 'price', 'photo', 'is_selected']

    def get_is_selected(self, topping):
        order_item = self.context.get('order_item')
        if order_item and hasattr(order_item, 'topping'):
            return topping in order_item.topping.all()
        return False


class ReOrderProductSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    product_sizes = serializers.SerializerMethodField()
    category_slug = serializers.CharField(source='category.slug')
    category_name = serializers.CharField(source='category.name')

    toppings = ReOrderToppingSerializer(many=True, read_only=True)

    def get_photo(self, obj):
        request = self.context.get('request')
        if request:
            if hasattr(obj, 'photo'):
                return request.build_absolute_uri(obj.photo.url) if obj.photo else None
        else:
            return None

    def get_product_sizes(self, obj):
        return ReOrderProductSizeSerializer(obj.product_sizes.all(), many=True).data

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'tags', 'toppings',
                  'product_sizes', 'category_slug', 'category_name']


class ReOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    def get_product(self, obj):
        return ReOrderProductSerializer(obj.product_size.product,
                                        context={'request': self.context.get('request'),
                                                 'order_item': obj}).data

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'total_amount', 'is_bonus']


class ReOrderSerializer(serializers.ModelSerializer):
    order_items = ReOrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Order
        fields = ['id', 'order_time', 'total_amount', 'order_items', 'payment_method',
                  'order_status', 'comment']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        order_items_serializer = ReOrderItemSerializer(instance.order_items.all(), many=True,
                                                       context={'request': self.context.get('request')})
        ret['order_items'] = order_items_serializer.data
        return ret


class OrderChatSerializer(OrderSerializer):
    order_items = ReOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_time', 'total_amount', 'is_pickup',
            'order_status', 'order_items', 'payment_method', 'change', 'order_source', 'comment',
            'promo_code'
        ]
