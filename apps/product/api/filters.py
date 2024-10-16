import django_filters

from apps.product.models import Product

from django.db.models import Q, Avg


class ProductFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(field_name='id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country__name', lookup_expr='icontains')  # Учитывая, что страна теперь связана
    category = django_filters.CharFilter(method='filter_final_category')
    gender = django_filters.CharFilter(field_name='gender__name', lookup_expr='iexact')  # Теперь `gender` — это ForeignKey

    # Используем CharFilter для фильтрации размеров через запятую
    size = django_filters.CharFilter(method='filter_by_size')

    price_min = django_filters.NumberFilter(method='filter_by_min_price')
    price_max = django_filters.NumberFilter(method='filter_by_max_price')
    rating_min = django_filters.NumberFilter(method='filter_by_average_rating')

    class Meta:
        model = Product
        fields = ['id', 'name', 'country', 'category', 'gender', 'size', 'price_min', 'price_max', 'rating_min']

    def filter_final_category(self, queryset, name, value):
        # Фильтруем только по конечной категории, которая не имеет подкатегорий
        return queryset.filter(category__name=value, category__subcategories__isnull=True)

    def filter_by_size(self, queryset, name, value):
        # Фильтруем продукты по размерам, связанным через таблицу `ProductSize`
        size_values = [s.strip() for s in value.split(',')]
        return queryset.filter(product_sizes__size__name__in=size_values).distinct()

    def filter_by_average_rating(self, queryset, name, value):
        # Фильтрация по среднему рейтингу отзывов на продукт
        return queryset.annotate(average_rating=Avg('product_reviews__rating')).filter(average_rating__gte=value)

    def filter_by_min_price(self, queryset, name, value):
        # Фильтрация по минимальной цене: смотрим только на discounted_price, а если его нет — на price
        return queryset.filter(
            Q(discounted_price__gte=value) | (Q(discounted_price__isnull=True) & Q(price__gte=value))
        )

    def filter_by_max_price(self, queryset, name, value):
        # Фильтрация по максимальной цене: смотрим только на discounted_price, а если его нет — на price
        return queryset.filter(
            Q(discounted_price__lte=value) | (Q(discounted_price__isnull=True) & Q(price__lte=value))
        )
