from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (ShopIndexView,
                    GroupsListView,
                    ProductDetailsView,
                    ProductsListView,
                    OrdersListView,
                    OrderDetailsView,
                    ProductCreateView,
                    ProductUpdateView,
                    ProductDeleteView,
                    OrderCreateView,
                    OrderUpdateView,
                    OrderDeleteView,
                    ProductsDataExportView,
                    OrdersExportView,
                    ProductViewSet,
                    OrderViewSet,
                    LatestProductsFeed,
                    UserOrdersListView,
                    UserOrdersExportView,
                    )

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders_list"),
    path('users/<int:user_id>/orders/export/', UserOrdersExportView.as_view(), name='export_user_orders'),
    path("orders/export/", OrdersExportView.as_view(), name="orders-export"),
    path("orders/<int:pk>", OrderDetailsView.as_view(), name="orders_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/create", OrderCreateView.as_view(), name="order_create"),
    path("products/latest/feed/", LatestProductsFeed(), name="products_feed"),
]
