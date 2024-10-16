from decimal import Decimal

import django_filters

from apps.product.models import Product

from django.db.models import Q, Avg


class ProductFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country__name', lookup_expr='icontains')
    category = django_filters.CharFilter(method='filter_final_category')

    # Используем MultipleChoiceFilter для фильтрации по полам
    gender = django_filters.CharFilter(method='filter_by_gender')

    # Используем CharFilter для фильтрации размеров через запятую
    size = django_filters.CharFilter(method='filter_by_size')

    price_min = django_filters.NumberFilter(method='filter_by_min_price')
    price_max = django_filters.NumberFilter(method='filter_by_max_price')

    # Используем MultipleChoiceFilter для фильтрации по рейтингу
    rating_min = django_filters.MultipleChoiceFilter(method='filter_by_average_rating')

    class Meta:
        model = Product
        fields = ['id', 'name', 'country', 'category', 'gender', 'size', 'price_min', 'price_max', 'rating_min']

    def filter_final_category(self, queryset, name, value):
        return queryset.filter(category__name=value, category__subcategories__isnull=True)

    def filter_by_size(self, queryset, name, value):
        size_values = [s.strip() for s in value.split(',')]
        return queryset.filter(product_sizes__size__name__in=size_values).distinct()

    def filter_by_gender(self, queryset, name, value):
        gender_values = [g.strip() for g in value.split(',')]
        return queryset.filter(gender__name__in=gender_values).distinct()

    def filter_by_average_rating(self, queryset, name, value):
        rating_values = [float(r.strip()) for r in value.split(',')]  # Convert to float
        return queryset.annotate(average_rating=Avg('product_reviews__rating')).filter(average_rating__gte=min(rating_values))

    def filter_by_min_price(self, queryset, name, value):
        return queryset.filter(
            Q(discounted_price__gte=value) | (Q(discounted_price__isnull=True) & Q(price__gte=value))
        )

    def filter_by_max_price(self, queryset, name, value):
        return queryset.filter(
            Q(discounted_price__lte=value) | (Q(discounted_price__isnull=True) & Q(price__lte=value))
        )
