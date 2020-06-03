#Serializers file will have a serializer
# to help your View serializing data to your model

from rest_framework import serializers
from core.health_check import HealthCheck

class HealthCheckSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()

    class Meta:
        model = HealthCheck
        fields = '__all__'
