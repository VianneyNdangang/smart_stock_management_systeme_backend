from rest_framework import generics
from .models import Category
from permissions import PermissionCodes, HasPermission
from django.db.models import Q, Count, Max
from .serializers import CategoryWriteSerializer, CategorySummarySerializer, CategoryReadSerializer

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

    filterset_fields = ["level","is_active","created_at"]
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
