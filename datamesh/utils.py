from typing import Tuple

from datamesh.models import Relationship, JoinRecord, LogicModuleModel


def prepare_lookup_kwargs(
    is_forward_lookup: bool, relationship: Relationship, join_record: JoinRecord
) -> Tuple[LogicModuleModel, str]:
    """Find out if pk is id or uuid and prepare lookup according to direction."""
    if is_forward_lookup:
        related_model = relationship.related_model
        related_record_field = (
            'related_record_id'
            if join_record.related_record_id is not None
            else 'related_record_uuid'
        )
    else:
        related_model = relationship.origin_model
        related_record_field = (
            'record_id' if join_record.record_id is not None else 'record_uuid'
        )

    return related_model, related_record_field
