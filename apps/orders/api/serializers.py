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
from apps.product.models import ProductSize, Product, Size, Topping
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
    quantity = serializers.IntegerField(default=1)
    is_bonus = serializers.BooleanField(default=False)

    class Meta:
        model = OrderItem
        fields = ['product_size_id', 'color_id', 'size_id', 'quantity', 'is_bonus', 'product']

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
        return {
            'id': product.id,
            'name': product.name,
            'price': product.discounted_price if product.discounted_price else product.price,
            'image': product.photo.url if product.photo else None
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
        # Если у вас есть данные о номере телефона или имени неавторизованного пользователя
        elif obj.phone_number:
            return obj.phone_number
        return "Адрес не указан"

    def get_app_download_url(self, obj):
        return None  # Поле app_download_link было связано с моделью TelegramBotToken, которая была удалена


class OrderSerializer(serializers.ModelSerializer):
    products = ProductOrderItemSerializer(many=True, required=False)
    order_source = serializers.ChoiceField(choices=[('web', 'web'), ('mobile', 'mobile')], default='web')
    change = serializers.IntegerField(default=0)
    is_pickup = serializers.BooleanField(default=False)
    promo_code = serializers.CharField(required=False, allow_blank=True)
    user_address_id = serializers.IntegerField(required=False, allow_null=True)  # Для авторизованного

    class Meta:
        model = Order
        fields = [
            'id', 'order_time', 'total_amount', 'is_pickup', 'user_address_id', 'order_status',
            'products', 'payment_method', 'change', 'order_source', 'comment',
            'promo_code'
        ]
        read_only_fields = ['total_amount', 'order_time', 'order_status']

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
                order_item = OrderItem(order=order, product_size_id=product_data['product_size_id'],
                                       quantity=product_data['quantity'], is_bonus=product_data['is_bonus'])
                order_item.save()

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
