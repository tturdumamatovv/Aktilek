from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, permissions
from rest_framework.exceptions import NotFound
from django.db.models import F, Case, When, Avg
from django.db import models
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import FavoriteProductSerializer

from apps.product.api.filters import ProductFilter
from apps.product.api.serializers import (
    ProductSerializer,
    CategoryProductSerializer,
    CategoryOnlySerializer,
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
    queryset = Product.objects.filter(is_active=True)
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

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        product = self.get_object()
        product.views_count += 1
        product.save(update_fields=['views_count'])
        return response

    def get_serializer_context(self):
        # Добавляем request в контекст для сериализатора
        return {'request': self.request}


class ProductDetailBySlugView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        product = self.get_object()
        product.views_count += 1
        product.save(update_fields=['views_count'])
        return response

    def get_serializer_context(self):
        # Добавляем request в контекст для сериализатора
        return {'request': self.request}


class ProductBonusView(generics.ListAPIView):
    queryset = Product.objects.filter(bonus_price__gt=0)
    serializer_class =  ProductSerializer


class ProductListByCategorySlugView(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    ordering_fields = ['datetime', 'views_count', 'average_rating', 'final_price']
    ordering = ['-datetime']

    def get_queryset(self):
        slug = self.kwargs['slug']
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise NotFound("Категория не найдена")

        # Annotate final_price as either discounted_price or price
        queryset = Product.objects.filter(category=category, is_active=True).annotate(
            average_rating=Avg('product_reviews__rating'),
            final_price=Case(
                When(discounted_price__isnull=False, then=F('discounted_price')),
                default=F('price'),
                output_field=models.DecimalField()
            )
        )
        print(queryset.query)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        print("Ordering Parameter:", request.query_params.get('ordering', ''))
        filtered_queryset = self.filter_queryset(queryset)

        ordered_queryset = self.filter_backends[-1]().filter_queryset(request, filtered_queryset, self)
        print("Ordered Queryset SQL:", str(ordered_queryset.query))

        category = Category.objects.get(slug=self.kwargs['slug'])
        serializer = CategoryProductSerializer(category, context={'request': request})
        serializer_data = serializer.data
        serializer_data['products'] = ProductSerializer(ordered_queryset, many=True, context={'request': request}).data

        return Response(serializer_data)


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


class PromotedCategoryListView(generics.ListAPIView):
    serializer_class = CategoryOnlySerializer

    def get_queryset(self):
        # Получаем только категории, у которых is_promoted=True
        return Category.objects.filter(is_promoted=True)


class PopularProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_popular=True, is_active=True).order_by('?')


class NewProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(is_new=True, is_active=True).order_by('?')


class CheckProductSizes(generics.GenericAPIView):
    serializer_class = ProductSizeIdListSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            size_ids = serializer.validated_data['sizes']
            sizes = ProductSize.objects.filter(id__in=size_ids).select_related('product', 'size')

            # Подготовка данных с True/False
            response_data = {}
            for size in sizes:
                response_data[size.id] = size.quantity > 0

            # Проверяем отсутствующие размеры
            missing_sizes = set(size_ids) - set(response_data.keys())
            response_data.update({size_id: False for size_id in missing_sizes})

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            # Если продукт уже в избранном, удаляем его и возвращаем is_favorite = False
            favorite.delete()
            return Response({
                "message": "Продукт удален из избранного",
                "product_id": product_id,
                "is_favorite": False
            }, status=status.HTTP_200_OK)

        # Если продукт добавлен в избранное, возвращаем is_favorite = True
        return Response({
            "message": "Продукт добавлен в избранное",
            "product_id": product_id,
            "is_favorite": True
        }, status=status.HTTP_201_CREATED)


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



class UserReviewListView(generics.ListAPIView):
    serializer_class = ReviewCreateSerializer  # Используем существующий сериализатор отзывов
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только те отзывы, которые создал текущий пользователь
        return Review.objects.filter(user=self.request.user)

