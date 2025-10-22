from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    language_tag = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=32)
    country_code = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=8)
    timezone = serializers.IntegerField(required=False, allow_null=True, min_value=-1000,
                                        max_value=1000)


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, min_length=4, max_length=100)
    new_password = serializers.CharField(required=True, min_length=4, max_length=100)

    def validate_new_password(self, value):
        """
        Validate that the new password meets the requirements of the User model.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value