"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
from csv import DictWriter
import logging
from timeit import default_timer
from django.utils.decorators import method_decorator
from django.contrib.syndication.views import Feed
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.views import APIView

from .common import save_csv_products, save_csv_orders
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django import forms
from django.contrib.auth.models import Group, User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser
from .forms import GroupForm, ProductForm
from shopapp.models import Product, Order, ProductImage
from django.views import View
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .serializers import ProductSerializer, OrderSerializer

logger = logging.getLogger(__name__)


class LatestProductsFeed(Feed):
    title = "Latest products"
    description = "Updates on changes and additions to products"
    link = reverse_lazy("shopapp:products_list")

    def items(self):
        return Product.objects.order_by('-pk')[:5]

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.description


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    \n
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = [
        'name',
        'description',
    ]
    filterset_fields = [
        "name",
        "description",
        "price",
        "count",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "count",
        "discount",
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        print("Hello products list")
        return super().list(request, *args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "count",
            "discount",
            "archived",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(methods=['post'],
            detail=False,
            parser_classes=[MultiPartParser],
            )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = [
        'delivery_address',
        'promocode',
    ]
    filterset_fields = [
        'delivery_address',
        'promocode',
    ]
    ordering_fields = [
        'delivery_address',
        'promocode',
    ]

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "orders-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "delivery_address",
            "promocode",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for order in queryset:
            writer.writerow({
                field: getattr(order, field)
                for field in fields
            })
        return response

    def upload_csv(self, request: Request):
        orders = save_csv_orders(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        # log.debug("Products for shop index: %s", products)
        logger.info("Rendering shop index")
        print("shop index context: ", context)
        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm,
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = 'product'


class ProductsListView(LoginRequiredMixin, ListView):
    template_name = "shopapp/products.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"

    model = Product
    fields = "name", "description", "price", "count", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    # fields = "name", "description", "price", "count", "discount", "preview"
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )
        return response

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.object.created_by == self.request.user
        return has_edit_perm and created_by_current_user

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        suscess_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(suscess_url)


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        products = Product.objects.order_by('pk').all()
        if products_data is None:
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "count": product.count,
                    "discount": product.discount,
                    "archived": product.archived,
                    "created_by": product.created_by.pk
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailsView(PermissionRequiredMixin, DetailView):
    permission_required = "view_order"
    queryset = (Order.objects.
                select_related("user").
                prefetch_related("products")
                )


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode",
    success_url = reverse_lazy("shopapp:orders_list")

    def form_valid(self, form):
        form.instance.user = self.get_user()
        form.save()
        products = self.request.POST.getlist('products')
        form.instance.products.set(products)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

    def get_user(self):
        return self.request.user


class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:orders_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class OrdersExportView(View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        orders = Order.objects.all()
        data = {
            'orders': [
                {
                    'id': order.id,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_id': order.user_id,
                    'product_ids': [product.id for product in order.products.all()]
                }
                for order in orders
            ]
        }
        return JsonResponse(data)


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopapp/orders_list.html'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        self.owner = get_object_or_404(User, pk=user_id)
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class UserOrdersExportView(APIView):

    def get(self, request, user_id):
        cache_key = f'user_orders_{user_id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return JsonResponse(cached_data, safe=False)
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")

        orders = Order.objects.filter(user=user).order_by('-created_at')
        orders_data = OrderSerializer(orders, many=True).data

        response_data = {
            'user_id': user.id,
            'user_name': user.username,
            'orders': orders_data
        }
        cache.set(cache_key, response_data, timeout=3600)
        return JsonResponse(response_data, safe=False)
