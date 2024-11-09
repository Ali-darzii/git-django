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
    username = serializers.CharField(min_length=4, max_length=150, required=True)

    def validate_username(self, username: str):
        """
        Username may only contain alphanumeric characters
        or single hyphens
        and cannot begin or end with a hyphen
        """
        if not re.fullmatch(r"^[a-zA-Z](?!.*__)[a-zA-Z0-9_]*[a-zA-Z0-9]$", username):
            raise serializers.ValidationError(detail="Invalid username format.")
        return username


class SendOTPSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=4, max_length=150, required=True)

    class Meta:
        model = User
        fields = ("email", "username", "password")

    def validate_password(self, password: str):
        """
        password must contain at least 8 characters
        and need to be alphanumeric characters
        """
        if not re.fullmatch(r"^[a-zA-Z0-9]*$", password) or len(password) < 8:
            raise serializers.ValidationError(ErrorResponses.BAD_FORMAT)
        return password

    def validate_username(self, username):
        """
        Username may only contain alphanumeric characters
        or single hyphens
        and cannot begin or end with a hyphen
        """
        if not re.fullmatch(r"^[a-zA-Z](?!.*__)[a-zA-Z0-9_]*[a-zA-Z0-9]$", username):
            raise serializers.ValidationError(detail="Invalid username format.")
        return username

    def validate(self, attr):
        if self.context["request"].method == "PUT":
            tk = attr.get("tk")
            if tk is None:
                raise serializers.ValidationError("tk is required.")
            if not tk.isdigit():
                raise serializers.ValidationError("tk must be digit in string.")
        attrs = super(SendOTPSerializer, self).validate(attr)
        return attrs


class CheckOTPSerializer(serializers.ModelSerializer):
    tk = serializers.CharField(max_length=8, min_length=8, required=True)

    class Meta:
        model = User
        fields = ("tk", "email",)

    def validate_tk(self, tk):
        if not tk.isdigit():
            raise serializers.ValidationError(ErrorResponses.BAD_FORMAT)
        return tk


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(min_length=4, max_length=150, required=False)
    password = serializers.CharField(max_length=128, required=True)
         

    def validate(self, attrs):
        """ ether username or email must have given"""
        if attrs.get("email") is None and attrs.get("username") is None:
            raise serializers.ValidationError("Ether email or username must have given.")
        attrs = super(IsActiveSendOTPSerializer, self).validate(attrs)
        return attrs
