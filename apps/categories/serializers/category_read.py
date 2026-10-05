from rest_framework import serializers
from apps.categories.models import Category


class CategorySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]

        read_only_fields = fields


class CategoryReadSerializer(serializers.ModelSerializer):

    parent = CategorySummarySerializer( read_only = True, allow_null = True)
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "parent",
            "slug",
            "level",
            "is_active",
            "created_at"
        ]

        read_only_fields = fields

