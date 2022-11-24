from rest_framework import serializers

from Content.constants import CLASSROOM_ACTIONS, CLASSROOM_ACTIONS_REQUIRED_FIELDS
from Content.models import (
    AccessGroup)
from Users.constants import CLASSROOM_ROLES


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGroup
        fields = ['id', 'name', 'type', 'users']
        read_only = True

    users = serializers.ListField(required=False)


class ClassroomCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class ClassroomActionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    action = serializers.ChoiceField(CLASSROOM_ACTIONS)
    role = serializers.ChoiceField(CLASSROOM_ROLES, required=False)

    def validate(self, data):
        action = data['action']
        required_fields = CLASSROOM_ACTIONS_REQUIRED_FIELDS[action]
        for field in required_fields:
            if data.get(field, None) is None:
                raise serializers.ValidationError(f'{field} is required')
        return data


class ClassroomUpdateSerializer(serializers.Serializer):
    new_name = serializers.CharField(max_length=100, required=False)
    actions = ClassroomActionSerializer(many=True)


class ClassroomEnrollSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=32)
