# users/serializers.py
from rest_framework import serializers
from .models import CustomUser, Role, Permission, UserActivity

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['name', 'description']

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'title', 'description', 'date', 'icon']

class CustomUserSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Role.objects.all())
    permissions = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Permission.objects.all())
    activities = UserActivitySerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'name', 'email', 'phone', 'cpf', 'birth_date', 'address',
            'status', 'avatar', 'roles', 'permissions', 'created_at', 'activities'
        ]
        read_only_fields = ['created_at', 'activities']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value

    def validate_cpf(self, value):
        if value and CustomUser.objects.filter(cpf=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Este CPF já está em uso.")
        return value

    def create(self, validated_data):
        roles = validated_data.pop('roles', [])
        permissions = validated_data.pop('permissions', [])
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        user.roles.set(roles)
        user.permissions.set(permissions)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop('roles', None)
        permissions = validated_data.pop('permissions', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if roles is not None:
            instance.roles.set(roles)
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance