from rest_framework import serializers

from auth_module.models import User


class EmailCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class UserRegister(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "username",)

    def username_validate(self, username):
        """
        Username may only contain alphanumeric characters
        or single hyphens
        and cannot begin or end with a hyphen
        """
        pass
