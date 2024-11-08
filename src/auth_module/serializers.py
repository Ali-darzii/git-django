from rest_framework import serializers

from auth_module.models import User
import re

from utils.responses import ErrorResponses


class EmailCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class UserRegister(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "username",)


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)

    def validate_username(self, username: str):
        """
        Username may only contain alphanumeric characters
        or single hyphens
        and cannot begin or end with a hyphen
        """
        if not re.fullmatch(r"^[a-zA-Z](?!.*__)[a-zA-Z0-9_]*[a-zA-Z0-9]$", username):
            raise serializers.ValidationError(detail="Invalid username format.")
        return username
