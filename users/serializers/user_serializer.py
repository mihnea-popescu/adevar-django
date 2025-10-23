from rest_framework import serializers
from django.contrib.auth import password_validation
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={"min_length": "Password must be at least 8 characters long."}
    )
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "id", "password", "last_login", "username", "email", "phone_number",
            "date_of_birth", "first_name", "last_name", "is_staff", "language_tag",
            "country_code", "timezone", "last_activity", "created_at", "updated_at"
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "username": {"read_only": True},
            "is_staff": {"read_only": True},
            "language_tag": {"read_only": True},
            "country_code": {"read_only": True},
            "timezone": {"read_only": True},
            "last_activity": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate_password(self, value):
        # Use Django's built-in password validators
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        """Use Django's secure create_user() method."""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user