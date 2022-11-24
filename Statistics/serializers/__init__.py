from Statistics.models import (
    # Achievement,
    # ActivityLog,
    TrainerBlockLog,
    TrainerBlockProgress,
    ProductProgress
)

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class TrainerBlockLogSerializer(ModelSerializer):
    class Meta:
        model = TrainerBlockLog
        fields = '__all__'


class TrainerBlockProgressSerializer(ModelSerializer):
    class Meta:
        model = TrainerBlockProgress
        fields = '__all__'


class ProductProgressSerializer(ModelSerializer):
    class Meta:
        model = ProductProgress
        fields = '__all__'


class ActivityLogPostSerializer(serializers.Serializer):
    activity = serializers.CharField(max_length=20)
    meta = serializers.JSONField()
