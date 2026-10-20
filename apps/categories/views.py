from rest_framework import generics
from .models import Category
from permissions import PermissionCodes, HasPermission
from django.db.models import Q, Count, Max
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .serializers import CategoryWriteSerializer, CategorySummarySerializer, CategoryReadSerializer, CategoryDetailSerializer
from apps.products.serializers import ProductReadSerializer
from apps.products.models import Product

class CategoriesListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_CATEGORIES

        elif self.request.method == "POST": 
            self.required_permission = PermissionCodes.CREATE_CATEGORIES

        return [HasPermission()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryWriteSerializer
        return CategoryReadSerializer

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_active=Count("id", filter=Q(is_active=True)),
            total_inactive=Count("id", filter=Q(is_active=False)),
            total_root=Count("id", filter=Q(parent__isnull = True)),
            total_with_children=Count("id", filter=Q(children__isnull = False), distinct=True),
            total_without_children=Count("id", filter=Q(children__isnull = True)),
            max_level=Max("level")
        )

    filterset_fields = ["level","is_active","created_at","parent",]
    search_fields = ["name","slug"]
    ordering_fields = ["level","name","created_at"]

class CategoriesDetailView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    lookup_field = "id"

    def get_permissions(self):
        permission_map = {
            "GET": PermissionCodes.VIEW_CATEGORIES,
            "PUT": PermissionCodes.UPDATE_CATEGORIES,
            "PATCH": PermissionCodes.UPDATE_CATEGORIES,
            "DELETE": PermissionCodes.DELETE_CATEGORIES,
        }

        self.required_permission = permission_map.get(
            self.request.method
        )
        return [HasPermission()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CategoryReadSerializer
        return CategoryWriteSerializer

class CategoryProductsView(generics.ListAPIView):
    serializer_class = ProductReadSerializer

    filterset_fields = [
        "is_active",
        "created_at",
        "is_perishable",
    ]

    search_fields = [
        "name",
        "description",
        "slug",
        "number",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]

    # def get_permissions(self):
    #     self.required_permission = 
    #     return [HasPermission()]

    required_permission = [PermissionCodes.VIEW_PRODUCTS]
    def get_queryset(self):
        category = get_object_or_404(
            Category,
            id=self.kwargs["category_id"],
        )

        if not category.is_active:
            raise PermissionDenied(
                "Impossible de consulter les produits d'une catégorie inactive."
            )

        return (
            Product.objects
            .filter(
                category_assignements__category=category,
            )
            .select_related("created_by")
            .prefetch_related("variants")
            .distinct()
            .order_by("name", "id")
        )