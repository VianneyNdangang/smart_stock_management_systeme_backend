from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from ..models import User
from apps.warehouses.serializer import WarehouseSummarySerializer
from apps.warehouses.models import Warehouse

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8
    )

    warehouse_id = serializers.PrimaryKeyRelatedField(
        source="warehouse",
        queryset=Warehouse.objects.filter(
            deleted_at__isnull=True
        ),
        write_only=True,
        required=False,
        allow_null=True
    )

    warehouse = WarehouseSummarySerializer(
        read_only=True
    )

    class Meta:
        model= User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "warehouse",
            "warehouse_id",
            "password",
            "avatar",
            "role",
            "is_active",
            "created_at",
        ]        
        read_only_fields = ["id", "created_at", "warehouse"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            }
        }

    def validate_password(self, password):
        validate_password(
            password,
            self.instance
        )
        return password

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


    def to_internal_value(self, data):
        """
        Vérifie que tous les champs envoyés
        sont déclarés dans le serializer.
        """

        allowed_input_fields = {
            field_name
            for field_name, field in self.fields.items()
            if not field.read_only
        }
        
        received_fields = set(data.keys())

        unexpected_fields = received_fields - allowed_input_fields

        if unexpected_fields:
            errors = {
                field: ["Ce champ n'est pas autorisé."]
                for field in unexpected_fields
            }

            raise serializers.ValidationError(errors)

        return super().to_internal_value(data)

    
class UserSummarySerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone", "avatar"]