from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import FavoriteProductSerializer

from apps.product.api.filters import ProductFilter
from apps.product.api.serializers import (
    ProductSerializer,
    CategoryProductSerializer,
    CategoryOnlySerializer,
    ProductSizeWithBonusSerializer,
    ProductSizeSerializer,
    ProductSizeIdListSerializer,
    FavoriteProduct,
    ReviewCreateSerializer,
    ProductDetailSerializer
)
from apps.product.models import (
    Category,
    Product,
    ProductSize,
    Review,
)


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'

    def get_serializer_context(self):
        # Добавляем request в контекст для сериализатора
        return {'request': self.request}


class ProductDetailBySlugView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def get_serializer_context(self):
        # Добавляем request в контекст для сериализатора
        return {'request': self.request}


class ProductBonusView(generics.ListAPIView):
    queryset = Product.objects.filter(bonus_price__gt=0)
    serializer_class =  ProductSerializer


class ProductListByCategorySlugView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise NotFound("Категория не найдена")

        serializer = CategoryProductSerializer(category, context={'request': request})
        # set_serializer = SetSerializer(sets, many=True, context={'request': request})

        return Response(serializer.data)


# class SetListView(generics.ListAPIView):
#     serializer_class = SetSerializer
#
#     def get_queryset(self):
#         return Set.objects.prefetch_related(
#             'products__product__ingredients',
#             'products__product__toppings',
#             'products__size'
#         )


class CategoryListView(generics.ListAPIView):
    serializer_class = CategoryProductSerializer

    def get(self, request, *args, **kwargs):
        categories = Category.objects.prefetch_related('products', 'sets').all()
        serializer = CategoryProductSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryOnlyListView(generics.ListAPIView):
    serializer_class = CategoryOnlySerializer

    def get(self, request, *args, **kwargs):
        # Получаем только родительские категории (категории верхнего уровня)
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategoryOnlySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class PopularProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_popular=True)


class NewProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_new=True)


class CheckProductSizes(APIView):
    def post(self, request):
        serializer = ProductSizeIdListSerializer(data=request.data)
        if serializer.is_valid():
            size_ids = serializer.validated_data['sizes']
            sizes = ProductSize.objects.filter(id__in=size_ids).select_related('product', 'size')
            response_data = {size.id: size.id for size in sizes}

            missing_sizes = set(size_ids) - set(response_data.keys())
            response_data.update({size_id: None for size_id in missing_sizes})

            return Response(response_data)
        return Response(serializer.errors, status=400)


class ToggleFavoriteProductView(generics.GenericAPIView):
    serializer_class = FavoriteProductSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Не указан ID продукта"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Продукт не найден"}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = FavoriteProduct.objects.get_or_create(user=request.user, product=product)

        if not created:
            # Если продукт уже в избранном, удаляем его
            favorite.delete()
            return Response({"message": "Продукт удален из избранного"}, status=status.HTTP_200_OK)

        return Response({"message": "Продукт добавлен в избранное"}, status=status.HTTP_201_CREATED)


class FavoriteProductsListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Получаем все избранные продукты текущего пользователя
        return Product.objects.filter(favorited_by__user=self.request.user)


class CreateReviewView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticated]  # Только авторизованные пользователи могут удалять отзывы

    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({"detail": "You do not have permission to delete this review."}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response({"detail": "Review deleted successfully."}, status=status.HTTP_200_OK)
