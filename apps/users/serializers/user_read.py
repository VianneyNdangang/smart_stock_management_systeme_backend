from apps.users.models import User
from rest_framework import serializers
from apps.warehouses.serializer import WarehouseSummarySerializer
from .user_permission import PermissionSummarySerializer, GroupSummarySerializer

class UserReadSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSummarySerializer(read_only=True)
    groups = GroupSummarySerializer( many = True, read_only = True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "warehouse",
            "avatar",
            "role",
            "groups",
            "permissions",
            "is_active",
            "created_at",
        ]

        read_only_fields = fields

    
    def get_permissions(self, obj):
        return PermissionSummarySerializer(obj.user_permissions.all(), many = True).data