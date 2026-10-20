from django.contrib.auth.models import Group, Permission
from rest_framework import serializers


class PermissionSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
        ]



class GroupCreateSerializer(serializers.ModelSerializer):

    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    permissions = serializers.SerializerMethodField(
        read_only=True
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
        ]

    def get_permissions(self, obj):
        return PermissionSummarySerializer(
            obj.permissions.all(),
            many=True
        ).data

    def create(self, validated_data):
        permissions = validated_data.pop(
            "permission_ids",
            []
        )

        group = Group.objects.create(
            **validated_data
        )

        group.permissions.set(permissions)

        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop(
            "permission_ids",
            None
        )

        instance.name = validated_data.get(
            "name",
            instance.name
        )

        instance.save()

        if permissions is not None:
            instance.permissions.set(permissions)

        return instance
    

class GroupSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
        ]