from django.urls import path

from apps.product.api.views import (
    ProductListByCategorySlugView,
    CategoryListView,
    ProductSearchView,
    ProductBonusView,
    CategoryOnlyListView,
    PopularProducts,
    NewProducts,
    CheckProductSizes,
    FavoriteProductsListView,
    ToggleFavoriteProductView,
    CreateReviewView,
    FormCategoryDetailView,
    FormVariantCreateView,
    OrderRequestCreateView,
    ProductDetailView
)

urlpatterns = [
          path('product/search/', ProductSearchView.as_view(), name='product-search'),
          path('bonus/', ProductBonusView.as_view(), name='bonus-list'),
          path('category/<slug:slug>/', ProductListByCategorySlugView.as_view(), name='category'),
          path('categories/', CategoryListView.as_view(), name='category-list'),
          path('categories/only/', CategoryOnlyListView.as_view(), name='category-only-list'),
          path('popular/products/', PopularProducts.as_view(), name='popular-products'),
          path('check/products/', CheckProductSizes.as_view(), name='check-products'),
          path('new/products/', NewProducts.as_view(), name='popular-products'),
          path('favorites/toggle/', ToggleFavoriteProductView.as_view(), name='favorite-add-delete'),
          path('favorites/', FavoriteProductsListView.as_view(), name='favorite-products'),
          path('reviews/create/', CreateReviewView.as_view(), name='create-review'),
          path('form/<slug:slug>/', FormCategoryDetailView.as_view(), name='form-category-detail'),
          path('form-variants/', FormVariantCreateView.as_view(), name='form-variant-create'),
          path('order-request/', OrderRequestCreateView.as_view(), name='order-request'),
          path('product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]
