from django.utils import timezone

from rest_framework import serializers
from Users.models import User, AccessGroupUserRelation, BannedUser, USER_SEX_CHOICES


class AccessGroupUserRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGroupUserRelation
        fields = '__all__'


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        password = validated_data['password']

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.last_login = timezone.now()
        user.email = validated_data['username']
        user.save()

        return user


class UserAccountUpdateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'password',
            'identifier', 'first_name', 'last_name', 'username', 'nickname', 'email',
            'image', 'image_50', 'sex', 'date_of_birth',
        ]


class UserAccountGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'nickname', 'email',
            'image', 'sex', 'date_of_birth',
        ]
        # read_only_fields = ('username', )
        read_only = True


class UserUpdateInfoAccountSerializer(serializers.ModelSerializer):
    sex = serializers.ChoiceField(choices=USER_SEX_CHOICES)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'nickname', 'email',
            'image', 'sex', 'date_of_birth',
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nickname', 'email']

    # def create(self, validated_data):
    #     password = validated_data['password']
    #
    #     user = User.objects.create(**validated_data)
    #     user.set_password(password)
    #     user.last_login = timezone.now()
    #     user.email = validated_data['username']
    #     user.save()
    #
    #     return user


class LoginUserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'username': {'validators': []}, }
        fields = ['username', 'password']
        read_only = True


class UnprotectedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { 'username': {'validators': []}, }
        fields = '__all__'
        read_only = True


class ProtectedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { 'username': {'validators': []}, }
        exclude = ['password']
        read_only = True


class OtherUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { 'username': {'validators': []}, }
        fields = ['first_name', 'last_name', 'nickname']
        read_only = True


class MainInfoUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nickname', 'email', 'username', 'is_staff', 'coins', 'rating_stars']
        read_only = True

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        serializer['has_limits'] = BannedUser.objects.filter(user=instance).exists()
        serializer['nickname'] = instance.get_nickname()
        serializer['access_content'] = self.context.get('access', False)
        return serializer


class VKAuthRequestSerializer(serializers.Serializer):
    access_token = serializers.CharField(max_length=250)
