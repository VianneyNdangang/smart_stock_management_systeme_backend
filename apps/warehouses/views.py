from rest_framework import generics
from .models import Warehouse
from .serializer import WarehouseSerializer
from permissions import HasPermission, PermissionCodes

class WarehousesListCreateView(generics.ListCreateAPIView):
    queryset = Warehouse.objects.filter(deleted_at__isnull=True)
    serializer_class = WarehouseSerializer
    
    def get_permissions(self):
            if self.request.method == "GET":
                self.required_permission = PermissionCodes.VIEW_WAREHOUSES
    
            elif self.request.method == "POST":
                self.required_permission = PermissionCodes.CREATE_WAREHOUSES
    
            return [HasPermission()]
    
    pagination_class = None
    search_fields = [
        "name",
        "location",
    ]
    ordering_fields = [
        "name",
        "location",
        "created_at",
        "region",
    ]

class WarehouseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Warehouse.objects.filter(deleted_at__isnull=True)
    serializer_class = WarehouseSerializer
    lookup_field = "id"

    def get_permissions(self):
            permission_map = {
                "GET": PermissionCodes.VIEW_WAREHOUSES,
                "PUT": PermissionCodes.UPDATE_WAREHOUSES,
                "PATCH": PermissionCodes.UPDATE_WAREHOUSES,
                "DELETE": PermissionCodes.DELETE_WAREHOUSES,
            }
    
            self.required_permission = permission_map.get(
                self.request.method
            )
    
            return [HasPermission()]

    # def perform_destroy(self, instance):
    #     instance.deleted_at = timezone.now()
    #     instance.save(update_fields=["deleted_at"])