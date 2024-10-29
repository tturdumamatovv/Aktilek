from rest_framework import serializers, status
from rest_framework.response import Response

from django.db.models import Min, Max, Avg

from apps.orders.models import OrderItem
from apps.product.models import (
    Product,
    ProductSize,
    Topping,
    Category,
    Tag,
    FavoriteProduct,
    Color,
    Review,
    Characteristic,
    ProductImage,
    Size,
    Country,
    Gender,
    ReviewImage, SizeChart
)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']

class ToppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topping
        fields = ['id', 'name', 'price', 'photo']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price'])
        return representation


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['image']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'text_color', 'background_color']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image', 'color']

    def get_image(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductSizeSerializer(serializers.ModelSerializer):
    color_id = serializers.IntegerField(source='color.id')
    color_name = serializers.CharField(source='color.name')
    color_hex_code = serializers.CharField(source='color.hex_code')
    size = serializers.CharField(source='size.name')  # Один размер
    images = ProductImageSerializer(many=True, read_only=True, source='color_images')  # Извлечение изображений

    class Meta:
        model = ProductSize
        fields = ['id', 'color_id', 'color_name', 'color_hex_code', 'images', 'size',
                  'quantity', 'price', 'discounted_price', 'bonus_price']  # Добавляем поле images

    def get_images(self, obj):
        # Теперь изображения получаются напрямую от ProductSize
        return ProductImageSerializer(obj.color_images.all(), many=True, context=self.context).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price']) if representation['price'] else None
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
            'discounted_price'] else None
        representation['bonus_price'] = float(representation['bonus_price']) if representation['bonus_price'] else None
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()  # Поле для полного имени пользователя
    images = ReviewImageSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at', 'images']

    def get_username(self, obj):
        # Предполагаем, что у объекта user есть поле full_name
        if obj.user and obj.user.full_name:
            return obj.user.full_name  # Возвращаем полное имя пользователя
        return "User"

    def get_created_at(self, obj):
        # Преобразуем дату в формат день/месяц/год
        return obj.created_at.strftime('%d.%m.%Y')


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['name', 'value']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'logo']


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    is_ordered = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField()
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'meta_name', 'slug', 'description', 'quantity',
                  'meta_description', 'photo', 'meta_photo', 'tags',
                  'price', 'discounted_price', 'country', 'bonus_price',
                  'category_slug', 'category_name', 'is_favorite',
                  'average_rating', 'review_count', 'is_ordered', 'is_active']

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None

    def get_category_slug(self, obj):
        if obj.category:
            return obj.category.slug
        return None

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def get_is_favorite(self, obj):
        request = self.context.get('request', None)
        if request is None or not hasattr(request, 'user'):
            return False
        user = request.user
        if user.is_authenticated:
            return FavoriteProduct.objects.filter(user=user, product=obj).exists()
        return False

    def get_review_count(self, obj):
        # Подсчитываем количество комментариев, игнорируя пустые строки
        return obj.product_reviews.exclude(comment='').count()

    def get_average_rating(self, obj):
        return round(obj.product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price']) if representation['price'] else None
        representation['discounted_price'] = float(representation['discounted_price']) if representation['discounted_price'] else None
        representation['bonus_price'] = float(representation['bonus_price']) if representation['bonus_price'] else None
        return representation


class ProductSimpleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    is_ordered = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField()
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'photo', 'tags',
                  'price', 'discounted_price', 'country', 'bonus_price',
                  'category_slug', 'category_name', 'is_favorite',
                  'average_rating', 'review_count', 'is_ordered', 'is_active']

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None

    def get_category_slug(self, obj):
        if obj.category:
            return obj.category.slug
        return None

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def get_is_favorite(self, obj):
        request = self.context.get('request', None)
        if request is None or not hasattr(request, 'user'):
            return False
        user = request.user
        if user.is_authenticated:
            return FavoriteProduct.objects.filter(user=user, product=obj).exists()
        return False

    def get_review_count(self, obj):
        # Подсчитываем количество комментариев, игнорируя пустые строки
        return obj.product_reviews.exclude(comment='').count()

    def get_average_rating(self, obj):
        return round(obj.product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price']) if representation['price'] else None
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
            'discounted_price'] else None
        representation['bonus_price'] = float(representation['bonus_price']) if representation['bonus_price'] else None
        return representation


class SizeChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeChart
        fields = ['image']


class ProductDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    product_sizes = ProductSizeSerializer(many=True, read_only=True)
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True, source='product_reviews')
    characteristics = CharacteristicSerializer(many=True, read_only=True, source='product_characteristics')
    gender = GenderSerializer(read_only=True)
    country = CountrySerializer(read_only=True)
    is_ordered = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    images = ProductImageSerializer(many=True, read_only=True)
    similar_products = serializers.SerializerMethodField()
    size_chart = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'photo', 'images', 'tags',
                  'price', 'discounted_price', 'bonus_price', 'product_sizes',
                  'category_slug', 'category_name', 'is_favorite',
                  'reviews', 'characteristics', 'average_rating',
                  'review_count', 'gender', 'country', 'is_ordered', 'is_active', 'similar_products', 'size_chart']

    def get_size_chart(self, obj):
        request = self.context.get('request')
        if obj.size_chart:
            return {
                "image": request.build_absolute_uri(obj.size_chart.image.url)  # Формируем полный URL
            }
        return None

    def get_category_slug(self, obj):
        if obj.category:
            return obj.category.slug
        return None

    def get_category_name(self, obj):
        if obj.category:
            return obj.category.name
        return None

    def get_is_favorite(self, obj):
        request = self.context.get('request', None)
        if request is None or not hasattr(request, 'user'):
            return False
        user = request.user
        if user.is_authenticated:
            return FavoriteProduct.objects.filter(user=user, product=obj).exists()
        return False

    def get_average_rating(self, obj):
        return round(obj.product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0)

    def get_review_count(self, obj):
        return obj.product_reviews.exclude(comment='').count()

    def get_similar_products(self, obj):
        # Получаем не более 10 случайных похожих товаров
        similar_products = obj.similar_products.order_by('?')[:10]
        return ProductSimpleSerializer(similar_products, many=True, context=self.context).data

    def get_is_ordered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if the current user has an order item for this product
            return OrderItem.objects.filter(product_size__product=obj, order__user=request.user, is_ordered=True).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price']) if representation['price'] else None
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
            'discounted_price'] else None
        representation['bonus_price'] = float(representation['bonus_price']) if representation['bonus_price'] else None
        return representation


class SizeProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    size = serializers.StringRelatedField()

    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'price', 'discounted_price']


class SetProductSerializer(serializers.ModelSerializer):
    # ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', ]  # 'ingredients', ]


class ComboProductSerializer(serializers.ModelSerializer):
    product = SetProductSerializer()
    size = serializers.StringRelatedField()

    class Meta:
        model = ProductSize
        fields = ['product', 'size', 'price', 'discounted_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['price'] = float(representation['price'])
        representation['discounted_price'] = float(representation['discounted_price']) if representation[
                                                                                              'discounted_price'] is not None else None
        return representation


# class SetSerializer(serializers.ModelSerializer):
#     products = ComboProductSerializer(many=True)
#
#     class Meta:
#         model = Set
#         fields = ['id', 'name', 'description', 'photo', 'products', 'price', 'discounted_price', 'bonuses']

# def to_representation(self, instance):
#     representation = super().to_representation(instance)
#     representation['price'] = float(representation['price'])
#     representation['discounted_price'] = float(representation['discounted_price']) if representation[
#                                                                                           'discounted_price'] is not None else None
#     return representation


class CategoryProductSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    filters = serializers.SerializerMethodField()
    parent_category = serializers.SerializerMethodField()  # Новое поле для родительской категории

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image', 'parent_category', 'products', 'subcategories', 'filters']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_subcategories(self, obj):
        # Рекурсивно сериализуем подкатегории
        subcategories = obj.subcategories.all()
        serializer = CategoryProductSerializer(subcategories, many=True, context=self.context)
        return serializer.data

    def get_filters(self, obj):
        # Получаем все продукты в категории
        products = Product.objects.filter(category=obj, is_active=True)

        # Минимальная и максимальная цена
        price_min = products.aggregate(Min('discounted_price'))['discounted_price__min'] or \
                    products.aggregate(Min('price'))['price__min']
        price_max = products.aggregate(Max('discounted_price'))['discounted_price__max'] or \
                    products.aggregate(Max('price'))['price__max']

        # Список доступных размеров, убираем None
        sizes = list(filter(None, set(products.values_list('product_sizes__size__name', flat=True))))
        countries = list(filter(None, set(products.values_list('country__name', flat=True))))
        genders = list(filter(None, set(products.values_list('gender__name', flat=True))))
        colors = list(filter(None, set(products.values_list('product_sizes__color__name', flat=True))))

        # Получаем все средние рейтинги для всех продуктов
        average_ratings = list(
            products.annotate(average_rating=Avg('product_reviews__rating')).values_list('average_rating', flat=True))

        # Убираем None и создаем уникальные значения
        unique_ratings = set(filter(None, average_ratings))

        return {
            'price_min': price_min,
            'price_max': price_max,
            'sizes': sizes,  # Список размеров без None
            'countries': countries,  # Список стран без None
            'genders': genders,  # Список полов без None
            'colors': colors,  # Список цветов без None
            'average_ratings': list(unique_ratings)  # Возвращаем список уникальных рейтингов без None
        }

    def get_parent_category(self, obj):
        # Возвращаем данные родительской категории, если она существует
        if obj.parent:
            return {
                'id': obj.parent.id,
                'name': obj.parent.name,
                'slug': obj.parent.slug,
            }
        return None


class CategoryOnlySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # Обрабатываем URL для изображения

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image', 'subcategories']

    def get_subcategories(self, obj):
        # Рекурсивно сериализуем подкатегории
        subcategories = obj.subcategories.all()
        if subcategories.exists():
            return CategoryOnlySerializer(subcategories, many=True, context=self.context).data
        return []

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSizeWithBonusSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_description = serializers.CharField(source='product.description')
    product_photo = serializers.ImageField(source='product.photo')
    size = serializers.CharField(source='size.name')

    class Meta:
        model = ProductSize
        fields = ['product_name', 'product_description', 'product_photo', 'size', 'id', 'bonus_price']

    def get_bonus_price(self, obj):
        return obj.bonus_price

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['bonus_price'] = float(representation['bonus_price'])
        return representation



class ProductSizeIdListSerializer(serializers.Serializer):
    sizes = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of product size IDs"
    )


class FavoriteProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = FavoriteProduct
        fields = ['product_id', 'is_favorite']

    def get_is_favorite(self, obj):
        # Всегда возвращаем True, так как если запись есть, продукт в избранном
        return True


class ProductShortSerializer(serializers.ModelSerializer):
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'average_rating', 'review_count']

    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None

    def get_review_count(self, obj):
        # Подсчитываем количество комментариев, игнорируя пустые строки
        return obj.product_reviews.exclude(comment='').count()

    def get_average_rating(self, obj):
        return round(obj.product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0)


class ReviewCreateSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)  # Поле для изображений
    created_at = serializers.SerializerMethodField()
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    # product = ProductShortSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'product', 'images', 'created_at']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        # Проверка, чтобы пользователь мог оставить до 5 отзывов для одного продукта
        reviews_count = Review.objects.filter(user=user, product=data['product']).count()
        if reviews_count >= 5:
            raise serializers.ValidationError({"error": "Вы можете оставить не более 5 отзывов на этот продукт."})

        # Проверка диапазона рейтинга
        rating = data.get('rating')
        if rating is not None:
            if rating < 0.0 or rating > 5.0:
                raise serializers.ValidationError({"error": "Рейтинг должен быть в диапазоне от 0 до 5."})
            if not isinstance(rating, float):
                raise serializers.ValidationError({"error": "Рейтинг должен быть числом (можно с плавающей запятой)."})

        return data

    def get_created_at(self, obj):
        # Форматируем дату в виде день.месяц.год
        return obj.created_at.strftime('%d.%m.%Y')

    def create(self, validated_data):
        request = self.context.get('request')
        images = request.FILES.getlist('images')  # Получаем список файлов

        user = request.user
        validated_data['user'] = user
        review = super().create(validated_data)

        # Сохранение изображений
        for image in images:
            ReviewImage.objects.create(review=review, image=image)  # Сохраняем каждое изображение

        return review


class ReviewsGetSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False)  # Поле для изображений
    created_at = serializers.SerializerMethodField()
    product = ProductShortSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'product', 'images', 'created_at']

    def get_created_at(self, obj):
        # Форматируем дату в виде день.месяц.год
        return obj.created_at.strftime('%d.%m.%Y')
