from rest_framework import serializers
from workflow import models as wfm


class WorkflowLevel1Serializer(serializers.ModelSerializer):
    class Meta:
        model = wfm.WorkflowLevel1
        fields = '__all__'


class WorkflowLevelTypeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = wfm.WorkflowLevelType
        fields = '__all__'


class WorkflowLevelStatusSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = wfm.WorkflowLevelStatus
        fields = '__all__'


class WorkflowLevel2Serializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='level2_uuid', read_only=True)

    class Meta:
        model = wfm.WorkflowLevel2
        fields = '__all__'


class InternationalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = wfm.Internationalization
        fields = '__all__'


class WorkflowLevel2NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = wfm.WorkflowLevel2
        fields = ('level2_uuid', 'name')
        read_only_fields = ('level2_uuid',)


class WorkflowLevel2SortSerializer(serializers.ModelSerializer):
    class Meta:
        model = wfm.WorkflowLevel2Sort
        fields = '__all__'
        read_only_fields = ('level2_uuid',)


class WorkflowTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'


class WorkflowTeamListFullSerializer(serializers.ModelSerializer):
    workflowlevel1 = WorkflowLevel1Serializer()

    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'
