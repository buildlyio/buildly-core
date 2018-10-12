from rest_framework import serializers

from . import models as gtm


class LogicModuleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()

    class Meta:
        model = gtm.LogicModule
        fields = '__all__'
