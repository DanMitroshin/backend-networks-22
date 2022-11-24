from rest_framework import serializers


class NamesSearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=100, help_text="Query search")
