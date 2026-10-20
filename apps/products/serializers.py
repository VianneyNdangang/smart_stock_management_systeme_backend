from django.db import transaction
from rest_framework import serializers
from apps.users.serializers import UserSummarySerializer
from apps.categories.serializers import CategorySummarySerializer
from apps.products.models import (
    Product,
    Variant,
    Attribute,
    AttributeValue,
    VariantAttributeValue,
    VariantImage,
    CategoryProduct,
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "number"
            "description",
            "image",
            "is_active",
            "is_perishable",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = [
            "id",
            "name",
        ]
        read_only_fields = [
            "id",
        ]


class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = [
            "id",
            "attribute",
            "value",
        ]
        read_only_fields = [
            "id",
        ]


class VariantAttributeInputSerializer(serializers.Serializer):
    attribute = serializers.CharField()
    value = serializers.CharField()

    def validate(self, attrs):
        attribute_name = attrs["attribute"].strip()
        value = attrs["value"].strip()

        try:
            attribute = Attribute.objects.get(
                name__iexact=attribute_name,
            )
        except Attribute.DoesNotExist:
            raise serializers.ValidationError({
                "attribute": (
                    f"L'attribut '{attribute_name}' n'existe pas."
                )
            })

        try:
            attribute_value = AttributeValue.objects.get(
                attribute=attribute,
                value__iexact=value,
            )
        except AttributeValue.DoesNotExist:
            raise serializers.ValidationError({
                "value": (
                    f"La valeur '{value}' n'existe pas pour "
                    f"l'attribut '{attribute.name}'."
                )
            })

        attrs["attribute_value"] = attribute_value

        return attrs


class VariantSerializer(serializers.ModelSerializer):
    attribute_values = VariantAttributeInputSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Variant
        fields = [
            "id",
            "price",
            "name",
            "sku",
            "barcode",
            "is_active",
            "attribute_values",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_attribute_values(self, attribute_values):
        attribute_ids = set()

        for item in attribute_values:
            attribute = item["attribute_value"].attribute

            if attribute.id in attribute_ids:
                raise serializers.ValidationError(
                    f"L'attribut '{attribute.name}' "
                    "ne peut apparaître qu'une seule fois."
                )

            attribute_ids.add(attribute.id)

        return attribute_values

    @transaction.atomic
    def create(self, validated_data):
        attribute_values = validated_data.pop(
            "attribute_values"
        )

        variant = Variant.objects.create(
            **validated_data
        )

        VariantAttributeValue.objects.bulk_create(
            [
                VariantAttributeValue(
                    variant=variant,
                    attribute_value=item["attribute_value"],
                )
                for item in attribute_values
            ]
        )

        return variant


class VariantCreateNestedSerializer(
    serializers.ModelSerializer
):
    attribute_values = VariantAttributeInputSerializer(
        many=True,
        write_only=True,
    )

    class Meta:
        model = Variant
        fields = [
            "name",
            "sku",
            "barcode",
            "is_active",
            "attribute_values",
        ]

    def validate_attribute_values(self, attribute_values):
        attribute_ids = set()

        for item in attribute_values:
            attribute = item["attribute_value"].attribute

            if attribute.id in attribute_ids:
                raise serializers.ValidationError(
                    f"L'attribut '{attribute.name}' "
                    "ne peut apparaître qu'une seule fois."
                )

            attribute_ids.add(attribute.id)

        return attribute_values


class VariantAttributeValueSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = VariantAttributeValue
        fields = [
            "id",
            "variant",
            "attribute_value",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]


class VariantAttributeValueDetailSerializer(
    serializers.ModelSerializer
):
    attribute = serializers.CharField(
        source="attribute_value.attribute.name",
        read_only=True,
    )

    value = serializers.CharField(
        source="attribute_value.value",
        read_only=True,
    )

    class Meta:
        model = VariantAttributeValue
        fields = [
            "attribute",
            "value",
        ]
        read_only_fields = [
            "attribute",
            "value",
        ]


class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = [
            "id",
            "variant",
            "alt_text",
            "is_primary",
            "position"
        ]
        read_only_fields = [
            "id"
        ]


class VariantDetailSerializer(
    serializers.ModelSerializer
):
    attributes = VariantAttributeValueDetailSerializer(
        source="attribute_values",
        many=True,
        read_only=True,
    )
    images = VariantImageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Variant
        fields = [
            "id",
            # "product",
            "name",
            "sku",
            "barcode",
            "price",
            "images",
            "attributes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "attributes",
            "created_at",
            "updated_at",
        ]

class CategoryProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(read_only = True)
    class Meta:
        model = CategoryProduct
        fields = [
            "category",
        ]
        read_only_fields = fields


class ProductDetailSerializer(serializers.ModelSerializer):
    variants = VariantDetailSerializer(
        many=True,
        read_only=True,
    )

    categories = serializers.SerializerMethodField()

    created_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "number",
            "name",
            "slug",
            "description",
            "categories",
            "image",
            "is_perishable",
            "is_active",
            "variants",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_categories(self, obj):
        assignments = obj.category_assignements.select_related("category")
        categories = [assignment.category for assignment in assignments]

        return CategorySummarySerializer(
            categories,
            many=True,
            context=self.context,
        ).data

    
class ProductReadSerializer(serializers.ModelSerializer):
    created_by = UserSummarySerializer(read_only = True)
    class Meta:
            model = Product
            fields = [
                "id",
                "name",
                "slug",
                "description",
                "image",
                "is_perishable",
                "is_active",
                "created_by",
                "created_at",
            ]
    
            read_only_fields = fields


class ProductCreateSerializer(
    serializers.ModelSerializer
):
    variants = VariantCreateNestedSerializer(
        many=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "is_perishable",
            "is_active",
            "image",
            "variants",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, request, validated_data):
        variants_data = validated_data.pop(
            "variants",
            [],
        )
        # created_by = request.user.id

        product = Product.objects.create(
            **validated_data
        )

        variant_assignments = []

        for variant_data in variants_data:
            attribute_values = variant_data.pop(
                "attribute_values",
                [],
            )

            variant = Variant.objects.create(
                product=product,
                **variant_data,
            )

            variant_assignments.extend(
                VariantAttributeValue(
                    variant=variant,
                    attribute_value=item["attribute_value"],
                )
                for item in attribute_values
            )

        VariantAttributeValue.objects.bulk_create(
            variant_assignments
        )

        return product