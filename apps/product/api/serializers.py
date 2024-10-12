from rest_framework import serializers
from django.db.models import Avg

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
    Ornament,
    Form,
    FormVariant,
    FormColor,
    FormCategory,
    Attribute,
    AttributeField,
    OrderRequest,
    ProductImage,
    Size
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
        image_url = obj.image.url
        if request is not None:
            return request.build_absolute_uri(image_url)
        return image_url


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductSizeSerializer(serializers.ModelSerializer):
    color = ColorSerializer()
    sizes = SizeSerializer(many=True)
    images = ProductImageSerializer(many=True, source='color.color_images')

    class Meta:
        model = ProductSize
        fields = ['id', 'color', 'images', 'sizes']

    def get_images(self, obj):
        # Получаем изображения, связанные с цветом
        images = ProductImage.objects.filter(color=obj.color)
        return ProductImageSerializer(images, many=True).data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user', 'rating', 'comment', 'created_at']


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['name', 'value']


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'tags',
                  'price', 'discounted_price',
                  'category_slug', 'category_name', 'is_favorite', 'average_rating']

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

    def get_average_rating(self, obj):
        return round(obj.product_reviews.aggregate(Avg('rating'))['rating__avg'] or 0)


class ProductDetailSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    product_sizes = ProductSizeSerializer(many=True, read_only=True)
    category_slug = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True, source='product_reviews')  # Предположим, что ReviewSerializer уже существует
    characteristics = CharacteristicSerializer(many=True, read_only=True, source='product_characteristics')  # Предположим, что CharacteristicSerializer уже существует

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'photo', 'tags',
                  'price', 'discounted_price', 'product_sizes',
                  'category_slug', 'category_name', 'is_favorite',
                  'reviews', 'characteristics', 'average_rating']

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
    # sets = SetSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'image', 'products', 'subcategories']  # 'sets']

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
        fields = ['product_name', 'product_description', 'product_photo', 'size', 'id']


class ProductSizeIdListSerializer(serializers.Serializer):
    sizes = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of product size IDs"
    )


class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = ['id', 'user', 'product']
        read_only_fields = ['user']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'product']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        # Проверка, чтобы пользователь не мог оставить более одного отзыва для одного продукта
        if Review.objects.filter(user=user, product=data['product']).exists():
            raise serializers.ValidationError("Вы уже оставляли отзыв на этот продукт.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        validated_data['user'] = user
        return super().create(validated_data)


class OrnamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ornament
        fields = ['id', 'name', 'image']

class FormColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormColor
        fields = ['id', 'name', 'hex_code']

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'type']

class FormVariantSerializer(serializers.ModelSerializer):
    color = FormColorSerializer()
    ornament = OrnamentSerializer()

    class Meta:
        model = FormVariant
        fields = ['id', 'name', 'logo', 'color', 'ornament']

class FormSerializer(serializers.ModelSerializer):
    ornaments = OrnamentSerializer(many=True)
    form_color = FormColorSerializer(many=True)
    attribute = AttributeSerializer(many=True)
    variants = FormVariantSerializer(many=True, source='formvariant_set')

    class Meta:
        model = Form
        fields = ['id', 'name', 'image', 'category', 'ornaments', 'form_color', 'attribute', 'variants']

class FormCategorySerializer(serializers.ModelSerializer):
    forms = FormSerializer(many=True)

    class Meta:
        model = FormCategory
        fields = ['id', 'name', 'description', 'slug', 'forms']


class FormVariantCreateSerializer(serializers.ModelSerializer):
    # Ссылки на связанные объекты передаются по их ID
    color_id = serializers.PrimaryKeyRelatedField(queryset=FormColor.objects.all(), source='color')
    ornament_id = serializers.PrimaryKeyRelatedField(queryset=Ornament.objects.all(), source='ornament')
    form_id = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all(), source='form')
    attribute_fields_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=AttributeField.objects.all(), source='attribute_fields')

    class Meta:
        model = FormVariant
        fields = ['name', 'logo', 'color_id', 'ornament_id', 'form_id', 'attribute_fields_ids']

    def create(self, validated_data):
        attribute_fields = validated_data.pop('attribute_fields')
        form_variant = FormVariant.objects.create(**validated_data)
        form_variant.attribute_fields.set(attribute_fields)
        return form_variant


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = ['full_name', 'email', 'phone_number', 'city_region', 'quantity', 'delivery_date', 'comments']
