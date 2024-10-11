import django_filters
from apps.product.models import Product
from django.db.models import Avg


class ProductFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    category = django_filters.CharFilter(method='filter_final_category')
    gender = django_filters.CharFilter(field_name='gender', lookup_expr='iexact')

    # Используем CharFilter для фильтрации размеров через запятую
    size = django_filters.CharFilter(method='filter_by_size')

    price_min = django_filters.NumberFilter(field_name='product_sizes__price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='product_sizes__price', lookup_expr='lte')
    rating_min = django_filters.NumberFilter(method='filter_by_average_rating')

    class Meta:
        model = Product
        fields = ['id', 'name', 'country', 'category', 'gender', 'size', 'price_min', 'price_max', 'rating_min']

    def filter_final_category(self, queryset, name, value):
        return queryset.filter(category__name=value, category__subcategories__isnull=True)

    def filter_by_size(self, queryset, name, value):
        size_values = [s.strip() for s in value.split(',')]
        return queryset.filter(product_sizes__size__name__in=size_values)

    def filter_by_rating(self, queryset, name, value):
        return queryset.filter(product_reviews__rating__gte=value).distinct()

    def filter_by_average_rating(self, queryset, name, value):
        return queryset.annotate(average_rating=Avg('product_reviews__rating')).filter(average_rating__gte=value)
