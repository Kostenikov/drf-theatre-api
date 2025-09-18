from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
        label=_("Password"),
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "is_staff")
        read_only_fields = ("id", "is_staff")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        username = validated_data.pop("username", instance.username)
        email = validated_data.pop("email", instance.email)
        password = validated_data.pop("password", None)

        instance.username = username
        instance.email = email

        if password:
            instance.set_password(password)

        instance.save()

        return instance
