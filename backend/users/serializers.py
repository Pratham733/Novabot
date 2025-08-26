from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "display_name"]
        read_only_fields = ["id"]

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    display_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    # Accept password1 as an alias for convenience (common client payloads)
    password1 = serializers.CharField(write_only=True, required=False)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # Unique username
        username = attrs.get("username", "").strip()
        if not username:
            raise serializers.ValidationError({"username": "This field is required."})
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "Username already taken"})

        # Unique email (if provided)
        email = attrs.get("email")
        if email:
            email = email.strip().lower()
            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError({"email": "Email already in use"})
            attrs["email"] = email

        # Password normalization & match
        pwd = attrs.get("password") or attrs.get("password1")
        pwd2 = attrs.get("password2")
        if not pwd:
            raise serializers.ValidationError({"password": "This field is required."})
        if pwd != pwd2:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        attrs["password"] = pwd
        attrs.pop("password1", None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
