from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "full_name")

    @staticmethod
    def get_full_name(obj):
        return f"{obj.first_name} {obj.last_name}"


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "token",
        )
