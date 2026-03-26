import re
from rest_framework import serializers
from .models import User, AnonymousIdentity
from .utils import generate_nickname, generate_avatar_seed


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    student_id = serializers.CharField(max_length=30)
    real_name = serializers.CharField(max_length=50)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已注册')
        return value

    def validate_password(self, value):
        if not re.search(r'[a-zA-Z]', value) or not re.search(r'[0-9]', value):
            raise serializers.ValidationError('密码必须包含字母和数字')
        return value

    def validate_student_id(self, value):
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError('学号/工号只能包含字母和数字')
        if User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError('该学号/工号已被注册')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            student_id=validated_data['student_id'],
            real_name=validated_data['real_name'],
        )
        AnonymousIdentity.objects.create(
            user=user,
            nickname=generate_nickname(),
            avatar_seed=generate_avatar_seed(),
        )
        return user


class AnonymousIdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnonymousIdentity
        fields = ['id', 'nickname', 'avatar_seed', 'created_at']


class UserInfoSerializer(serializers.ModelSerializer):
    default_identity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'student_id', 'is_verified', 'date_joined', 'default_identity']

    def get_default_identity(self, obj):
        identity = obj.identities.order_by('-created_at').first()
        if identity:
            return AnonymousIdentitySerializer(identity).data
        return None
