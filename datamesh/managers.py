from typing import Any

from django.db.models import Manager, QuerySet, Model
from django.db.models.functions import Concat

from gateway import utils


class LogicModuleModelManager(Manager):
    def get_by_concatenated_model_name(self, concatenated_model_name: str) -> Model:
        return (
            self.annotate(
                swagger_model_name=Concat('logic_module_endpoint_name', 'model')
            )
            .filter(swagger_model_name=concatenated_model_name)
            .first()
        )


class JoinRecordManager(Manager):
    def get_join_records(
        self, origin_pk: Any, relationship: Model, is_forward_relationship: bool
    ) -> QuerySet:
        """Get JoinRecords for relation on origin_pk in a certain direction."""
        if utils.valid_uuid4(str(origin_pk)):
            pk_field = 'record_uuid'
        else:
            pk_field = 'record_id'
        if not is_forward_relationship:
            pk_field = 'related_' + pk_field

        return self.filter(relationship=relationship).filter(
            **{pk_field: str(origin_pk)}
        )
