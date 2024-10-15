import pytz
from django.db import transaction
from django.conf import settings
from rest_framework import serializers
from apps.orders.models import (
    Order,
    OrderItem,
    Report,
    PromoCode
)
from apps.product.models import ProductSize, Product, Size, Topping, Color
from django.utils.translation import gettext_lazy as _


class ToppingSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Topping
        fields = ['id', 'name', 'price']


class ProductOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    product_size_id = serializers.IntegerField(write_only=True)
    color_id = serializers.IntegerField(write_only=True)
    size_id = serializers.IntegerField(write_only=True)
    color = serializers.SerializerMethodField(read_only=True)  # Поле для возврата выбранного цвета
    size = serializers.SerializerMethodField(read_only=True)
    quantity = serializers.IntegerField(default=1)
    is_bonus = serializers.BooleanField(default=False)

    class Meta:
        model = OrderItem
        fields = ['product_size_id', 'color_id', 'size_id', 'quantity', 'is_bonus', 'product', 'color', 'size']

    def validate(self, data):
        # Проверка на наличие product_size
        product_size_id = data.get('product_size_id')
        color_id = data.get('color_id')
        size_id = data.get('size_id')

        try:
            product_size = ProductSize.objects.get(id=product_size_id)
        except ProductSize.DoesNotExist:
            raise serializers.ValidationError(f"ProductSize with id {product_size_id} does not exist.")

        # Проверка соответствия цвета и размера
        if product_size.color.id != color_id:
            raise serializers.ValidationError("The selected color does not match the product size.")

        if not product_size.sizes.filter(id=size_id).exists():
            raise serializers.ValidationError("The selected size does not match the product size.")

        return data

    def get_product(self, obj):
        # Возвращает информацию о продукте
        product = obj.product_size.product
        request = self.context.get('request')  # Получаем контекст запроса
        image_url = product.photo.url if product.photo else None

        if request and image_url:
            image_url = request.build_absolute_uri(image_url)  # Строим полный URL

        return {
            'id': product.id,
            'name': product.name,
            'price': product.discounted_price if product.discounted_price else product.price,
            'image': image_url  # Возвращаем полный URL изображения
        }

    def get_color(self, obj):
        # Возвращаем информацию о цвете
        return {
            'id': obj.product_size.color.id,
            'name': obj.product_size.color.name,
            'hex_code': obj.product_size.color.hex_code,
        }

    def get_size(self, obj):
        # Возвращаем только выбранный размер
        chosen_size = obj.product_size.sizes.filter(id=obj.size_id).first()
        if chosen_size:
            return {'id': chosen_size.id, 'name': chosen_size.name}
        return None


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
    products = ProductOrderItemSerializer(many=True, required=False)
    order_source = serializers.ChoiceField(choices=[('web', 'web'), ('mobile', 'mobile')], default='web')
    change = serializers.IntegerField(default=0)
    is_pickup = serializers.BooleanField(default=False)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    user_address_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_time', 'total_amount', 'delivery_info', 'is_pickup', 'user_address_id', 'order_status',
            'products', 'payment_method', 'change', 'order_source', 'comment',
            'promo_code',
        ]
        read_only_fields = ['total_amount', 'order_time', 'order_status']

    def get_delivery_info(self, obj):
        # Условие для возврата информации о доставке
        if not obj.is_pickup:
            return "Уточните сумму доставки у оператора"
        return None

    def validate(self, data):
        # Если заказ не самовывоз и пользователь авторизован, проверяем, что указан user_address_id
        if not data.get('is_pickup') and self.context['request'].user.is_authenticated:
            if not data.get('user_address_id'):
                raise serializers.ValidationError({
                    "user_address_id": "Адрес пользователя обязателен для курьерской доставки."
                })
        return data

    def create(self, validated_data):
        products_data = validated_data.pop('products', [])
        promo_code_data = validated_data.pop('promo_code', None)
        user_address_id = validated_data.pop('user_address_id', None)  # Адрес для авторизованного

        # Save the order
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            # Если адрес для авторизованного пользователя передан
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
                # Получаем имя размера по его id
                try:
                    size = Size.objects.get(id=product_data['size_id'])
                    size_name = size.name  # Получаем имя размера
                except Size.DoesNotExist:
                    size_name = "Размер не найден"

                # Получаем имя цвета по его id
                try:
                    color = Color.objects.get(id=product_data['color_id'])
                    color_name = color.name  # Получаем имя цвета
                except Color.DoesNotExist:
                    color_name = "Цвет не найден"

                # Создаем OrderItem и сохраняем его с именами размера и цвета
                order_item = OrderItem(
                    order=order,
                    product_size_id=product_data['product_size_id'],
                    size_id=product_data['size_id'],
                    size_name=size_name,  # Сохраняем имя размера
                    color_id=product_data['color_id'],
                    color_name=color_name,  # Сохраняем имя цвета
                    quantity=product_data['quantity'],
                    is_bonus=product_data['is_bonus']
                )
                order_item.save()
                product = Product.objects.get(id=product_data['product_size_id'])  # Получаем продукт
                product.is_ordered = True  # Устанавливаем поле в True
                product.save()

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


class ReOrderProductSizeSerializer(serializers.ModelSerializer):
    size = serializers.CharField(source='size.name')
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False,
                                                allow_null=True)
    bonus_price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    is_selected = serializers.SerializerMethodField()

    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'price', 'discounted_price', 'bonus_price', 'is_selected']

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
        order_item = self.context.get('order_item')
        return ReOrderProductSizeSerializer(obj.product_sizes.all(), many=True, context={'order_item': order_item}).data

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
