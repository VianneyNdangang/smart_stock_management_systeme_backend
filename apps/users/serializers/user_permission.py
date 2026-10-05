from django.contrib.auth.models import Group, Permission
from rest_framework import serializers


class PermissionSummarySerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "codename",
            "content_type",
        ]

    def get_content_type(self, obj):
        return {
            "app_label": obj.content_type.app_label,
            "model": obj.content_type.model,
        }


class GroupSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = [
            "id",
            "name",
        ]