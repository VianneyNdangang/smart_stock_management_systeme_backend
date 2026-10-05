from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .bases import StrictModelSerializer
from django.contrib.auth.models import Group, Permission
from apps.users.models import User
from .user_permission import GroupSummarySerializer, PermissionSummarySerializer
from apps.warehouses.models import Warehouse
from apps.warehouses.serializer import WarehouseSummarySerializer


class UserCreateSerializer(StrictModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    warehouse = WarehouseSummarySerializer(read_only=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(
        source="warehouse",
        queryset=Warehouse.objects.filter(
            deleted_at__isnull=True
        ),
        required=False,
        allow_null=True,
        write_only=True,
    )

    group_ids = serializers.PrimaryKeyRelatedField(
        source="groups",
        queryset=Group.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    permission_ids = serializers.PrimaryKeyRelatedField(
        source="user_permissions",
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "warehouse_id",
            "password",
            "avatar",
            "warehouse",
            "group_ids",
            "permission_ids",
            "created_at",
            
        ]
        read_only_fields = ["id", "created_at"]

    def validate_password(self, password):
        validate_password(password)
        return password

    def create(self, validated_data):
        password = validated_data.pop("password")
        groups = validated_data.pop(
            "groups",
            []
        )

        permissions = validated_data.pop(
            "user_permissions",
            []
        )

        user = User(**validated_data)
        user.set_password(password)
        user.groups.set(groups)
        user.user_permissions.set(permissions)
        user.save()
        return user


class UserUpdateSerializer(StrictModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "avatar",
        ]
        read_only_fields = [
            "id"
        ]

class UserAdminUpdateSerializer(StrictModelSerializer):
    warehouse_id = serializers.PrimaryKeyRelatedField(
        source="warehouse",
        queryset=Warehouse.objects.filter(
            deleted_at__isnull=True
        ),
        required=False,
        allow_null=True,
        write_only=True,
    )
    group_ids = serializers.PrimaryKeyRelatedField(
        source="groups",
        queryset=Group.objects.all(),
        many=True,
        required=False,
        write_only=True
    )

    permission_ids = serializers.PrimaryKeyRelatedField(
        source="user_permissions",
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    warehouse = WarehouseSummarySerializer(read_only=True)
    groups = GroupSummarySerializer( many = True, read_only = True)
    permissions = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "warehouse_id",
            "avatar",
            "role",
            "is_active",
            "group_ids",
            "permission_ids",
            "warehouse",
            "groups",
            "permissions",
            "created_at",
        ]
        read_only_fields = ["id","created_at","groups","permissions",]

    def get_permissions(self, obj):
        return PermissionSummarySerializer(
            obj.user_permissions.all(),
            many=True
        ).data

    def update(self, instance, validated_data):

        groups = validated_data.pop(
            "groups",
            None
        )

        permissions = validated_data.pop(
            "user_permissions",
            None
        )

        instance = super().update(
            instance,
            validated_data
        )

        if groups is not None:
            instance.groups.set(groups)

        if permissions is not None:
            instance.user_permissions.set(permissions)

        return instance

class GroupCreateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source="permissions",
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    permissions = PermissionSummarySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "permission_ids",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "permissions",
        ]

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])

        group = Group.objects.create(**validated_data)

        if permissions:
            group.permissions.set(permissions)

        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    permission_ids = serializers.PrimaryKeyRelatedField(
        source="permissions",
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    permissions = PermissionSummarySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "permission_ids",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "permissions",
        ]

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions", None)

        instance = super().update(
            instance,
            validated_data
        )

        if permissions is not None:
            instance.permissions.set(permissions)

        return instance