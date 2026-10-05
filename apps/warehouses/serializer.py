from rest_framework import serializers
from .models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model= Warehouse
        fields= ["id", "name", "location", "region", "created_at"]
        read_only_fields= ["id", "created_at"]

class WarehouseSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "name"]