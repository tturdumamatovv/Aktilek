from django.urls import path
from .views import (
    CreateOrderView,
    OrderPreviewView,
    ReportCreateView,
    ListOrderView,
    PromoCodeDetailView,
    CreateReOrderView,
    get_user_orders,
    get_order_details
)

urlpatterns = [
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('orders/', ListOrderView.as_view(), name='order-list'),
    path('order-preview/', OrderPreviewView.as_view(), name='order-preview'),
    path('reports/', ReportCreateView.as_view(), name='create-report'),
    path('promocode/<str:code>/', PromoCodeDetailView.as_view(), name='promocode-detail'),
    path('reorder/<int:order_id>/', CreateReOrderView.as_view(), name='reorder'),
    path('user/orders/', get_user_orders, name='user_orders'),
    path('details/', get_order_details, name='get_order_details'),
]
