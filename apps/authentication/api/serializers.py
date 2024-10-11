from rest_framework import serializers

from apps.authentication.models import (
    User,
    UserAddress
)
from config import settings


class UserBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['bonus']


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'full_name', 'date_of_birth', 'email')
        read_only_fields = ('full_name', 'date_of_birth', 'email')


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
    fcm_token = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    receive_notifications = serializers.BooleanField(required=False, allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    has_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'phone_number', 'profile_picture', 'full_name', 'date_of_birth',
                  'email', 'first_visit', 'has_profile_picture', 'receive_notifications')
        read_only = ('receive_notifications',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if not ret['profile_picture']:
            if request is not None:
                ret['profile_picture'] = request.build_absolute_uri(
                    settings.MEDIA_URL + 'profile_pictures/default-user.jpg')
            else:
                ret['profile_picture'] = settings.MEDIA_URL + 'profile_pictures/default-user.jpg'
        return ret

    def get_has_profile_picture(self, instance):
        return bool(instance.profile_picture)


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary', 'longitude', 'latitude']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']


class UserAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [field.name for field in UserAddress._meta.fields if field.name not in ('id', 'user')]


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    city = serializers.CharField(required=False)
    is_primary = serializers.BooleanField(required=False)  # Include 'is_primary' as an optional field

    class Meta:
        model = UserAddress
        fields = ['id', 'user', 'city', 'apartment_number', 'entrance',
                  'floor', 'intercom', 'created_at', 'is_primary', 'longitude', 'latitude']  # Include 'is_primary'
        read_only_fields = ['user', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    fcm_token = serializers.CharField(max_length=255, required=False)
    receive_notifications = serializers.BooleanField(default=True, required=False)

    class Meta:
        model = User
        fields = ('fcm_token', 'receive_notifications')
