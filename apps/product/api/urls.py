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
    ProductDetailView,
    ReviewDeleteView,
    ProductDetailBySlugView,
    PromotedCategoryListView
)

urlpatterns = [
          path('product/search/', ProductSearchView.as_view(), name='product-search'),
          path('bonus/', ProductBonusView.as_view(), name='bonus-list'),
          path('category/<slug:slug>/', ProductListByCategorySlugView.as_view(), name='category'),
          path('categories/', CategoryListView.as_view(), name='category-list'),
          path('categories/only/', CategoryOnlyListView.as_view(), name='category-only-list'),
          path('promoted-categories/', PromotedCategoryListView.as_view(), name='promoted-categories'),
          path('popular/products/', PopularProducts.as_view(), name='popular-products'),
          path('check/products/', CheckProductSizes.as_view(), name='check-products'),
          path('new/products/', NewProducts.as_view(), name='popular-products'),
          path('favorites/toggle/', ToggleFavoriteProductView.as_view(), name='favorite-add-delete'),
          path('favorites/', FavoriteProductsListView.as_view(), name='favorite-products'),
          path('reviews/create/', CreateReviewView.as_view(), name='create-review'),
          path('product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
          path('products/<slug:slug>/', ProductDetailBySlugView.as_view(), name='product-detail-by-slug'),
          path('reviews/<int:pk>/', ReviewDeleteView.as_view(), name='review-delete'),
]
