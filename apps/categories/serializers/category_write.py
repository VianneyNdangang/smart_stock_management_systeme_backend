from rest_framework import serializers
from apps.categories.models import Category
from .category_read import CategorySummarySerializer

class CategoryWriteSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source="parent",
        queryset = Category.objects.all(),
        required= False,
        allow_null = True,
        write_only = True,
    )

    parent = CategorySummarySerializer( read_only = True)
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent_id",
            "parent",
            "level",
            "is_active",
            "created_at"
        ]
        read_only_fields = ["id","slug","created_at","parent","level"]
