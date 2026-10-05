from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .user_read import UserReadSerializer


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Email ou mot de passe incorrect."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": UserReadSerializer(
                user,
                context=self.context
            ).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )

    def validate_current_password(self, password):
        user = self.context["request"].user

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Le mot de passe actuel est incorrect."
            )

        return password

    def validate_new_password(self, password):
        user = self.context["request"].user

        validate_password(
            password,
            user,
        )

        if user.check_password(password):
            raise serializers.ValidationError(
                "Le nouveau mot de passe doit être différent de l'ancien."
            )

        return password