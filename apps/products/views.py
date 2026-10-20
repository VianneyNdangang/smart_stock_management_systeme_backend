from rest_framework import generics
from django.db.models import Q, Count
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from .models import Product, Variant, Attribute, AttributeValue
from .serializers import (
    ProductReadSerializer,
    ProductDetailSerializer,
    AttributeSerializer,
    AttributeValueSerializer,
    VariantDetailSerializer,
    VariantSerializer,
    ProductCreateSerializer,
)

from permissions import PermissionCodes, HasPermission


class ProductsListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_PRODUCTS

        elif self.request.method == "POST":
            self.required_permission = PermissionCodes.CREATE_PRODUCTS

        return [HasPermission()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductReadSerializer

        return ProductDetailSerializer

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_active=Count(
                "id",
                filter=Q(is_active=True),
            ),
            total_inactive=Count(
                "id",
                filter=Q(is_active=False),
            ),
            total_variants=Count(
                "variants",
                distinct=True,
            ),
            total_perishable_products=Count(
                "id",
                filter=Q(is_perishable=True),
                distinct=True,
            ),
            total_non_perishable_products=Count(
                "id",
                filter=Q(is_perishable=False),
            ),
        )

    filterset_fields = [
        "is_active",
        "created_at",
        "is_perishable",
    ]

    search_fields = [
        "name",
        "description",
        "slug",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]


class ProductsDetailView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    lookup_field = "id"

    def get_permissions(self):
        permission_map = {
            "GET": PermissionCodes.VIEW_PRODUCTS,
            "PUT": PermissionCodes.UPDATE_PRODUCTS,
            "PATCH": PermissionCodes.UPDATE_PRODUCTS,
        }

        self.required_permission = permission_map.get(
            self.request.method
        )

        return [HasPermission()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProductDetailSerializer
        return ProductCreateSerializer

class AttributeListCreateView(generics.ListCreateAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [IsAuthenticated]
    search_fields = [
        "name",
        "slug",
    ]

class AttributeValueListCreateView(generics.ListCreateAPIView):
    queryset = AttributeValue.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_ATTRIBUTE_VALUES

        elif self.request.method == "POST":
            self.required_permission = PermissionCodes.CREATE_ATTRIBUTE_VALUES

        return [HasPermission()]

    serializer_class = AttributeValueSerializer

    search_fields = [
        "value",
    ]

class VariantListCreateView(generics.ListCreateAPIView):
    def get_product(self):
        try:
            return Product.objects.get(
                id=self.kwargs["product_id"]
            )
        except Product.DoesNotExist:
            raise NotFound(
                "Le produit demandé n'existe pas."
            )

    def get_queryset(self):
        return Variant.objects.filter(
            product_id=self.kwargs["product_id"]
        ).select_related(
            "product"
        ).prefetch_related(
            "attribute_values__attribute_value__attribute"
        )

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_VARIANTS

        elif self.request.method == "POST":
            self.required_permission = PermissionCodes.CREATE_VARIANTS

        return [HasPermission()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VariantSerializer

        return VariantDetailSerializer

    def perform_create(self, serializer):
        product = self.get_product()

        serializer.save(
            product=product
        )