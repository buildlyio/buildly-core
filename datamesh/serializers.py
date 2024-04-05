from collections import OrderedDict

from rest_framework import serializers

from datamesh.models import JoinRecord, Relationship, LogicModuleModel


class LogicModuleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogicModuleModel
        fields = '__all__'


class RelationshipSerializer(serializers.ModelSerializer):

    origin_model = LogicModuleModelSerializer(read_only=True)
    related_model = LogicModuleModelSerializer(read_only=True)
    origin_model_id = serializers.UUIDField(write_only=True)
    related_model_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Relationship
        fields = '__all__'


class JoinRecordSerializer(serializers.ModelSerializer):
    """
    The model_choices are created based on the logic_module__name as a prefix and the model name.
    Example: locationSiteProfile
    """

    _model_choices = list()
    _model_choices_map = dict()

    origin_model_name = serializers.ChoiceField(choices=_model_choices, write_only=True)
    related_model_name = serializers.ChoiceField(
        choices=_model_choices, write_only=True
    )

    def __init__(self, *args, **kwargs):
        """Define the choices for valid LogicModuleModels."""
        for model in LogicModuleModel.objects.all().values(
            'logic_module_endpoint_name', 'model', 'pk'
        ):
            choice = model['logic_module_endpoint_name'] + model['model']
            self._model_choices.append(choice)
            self._model_choices_map.update({choice: model['pk']})
        super().__init__(*args, **kwargs)

    def create(self, validated_data: dict) -> JoinRecord:
        """Get logic_module_models, get_or_create `Relationship`s and save in case it is not already existing."""
        origin_model_pk = self._model_choices_map[
            validated_data.pop('origin_model_name')
        ]
        related_model_pk = self._model_choices_map[
            validated_data.pop('related_model_name')
        ]
        relationship, _ = Relationship.objects.get_or_create(
            origin_model_id=origin_model_pk, related_model_id=related_model_pk
        )
        organization_uuid = self.context['request'].session.get(
            'jwt_organization_uuid', None
        )
        join_record, _ = JoinRecord.objects.get_or_create(
            relationship=relationship,
            organization_id=organization_uuid,
            **validated_data,
        )
        return join_record

    def update(self, instance: JoinRecord, validated_data: dict) -> JoinRecord:
        """Automatically set the relationship from the passed models."""
        origin_model_pk = self._model_choices_map[
            validated_data.pop('origin_model_name')
        ]
        related_model_pk = self._model_choices_map[
            validated_data.pop('related_model_name')
        ]
        relationship, _ = Relationship.objects.get_or_create(
            origin_model_id=origin_model_pk, related_model_id=related_model_pk
        )
        instance.relationship = relationship
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def to_representation(self, instance: JoinRecord) -> OrderedDict:
        """Add origin_model_name and related_model_name."""
        ret_repr = super().to_representation(instance)
        ret_repr.update(
            {
                'origin_model_name': f'{instance.relationship.origin_model.logic_module_endpoint_name}'
                f'{instance.relationship.origin_model.model}',
                'related_model_name': f'{instance.relationship.related_model.logic_module_endpoint_name}'
                f'{instance.relationship.related_model.model}',
            }
        )
        return ret_repr

    class Meta:
        model = JoinRecord
        exclude = ('relationship',)
        read_only_fields = ('organization',)
