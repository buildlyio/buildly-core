from typing import Any

from django.db.models import Manager, QuerySet, Model

from gateway import utils


class JoinRecordManager(Manager):

    def get_join_records(self,
                         origin_pk: Any,
                         relationship: Model,
                         is_forward_relationship: bool) -> QuerySet:
        """Get JoinRecords for relation on origin_pk in a certain direction."""
        if utils.valid_uuid4(str(origin_pk)):
            pk_field = 'record_uuid'
        else:
            pk_field = 'record_id'
        if not is_forward_relationship:
            pk_field = 'related_' + pk_field

        return self.filter(relationship=relationship).filter(**{pk_field: str(origin_pk)})
