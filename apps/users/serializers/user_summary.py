from rest_framework import serializers

from apps.users.models import User


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "avatar",
            "email",
        ]
        read_only_fields = [
            "id",
        ]