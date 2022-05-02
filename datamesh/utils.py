from typing import Tuple

from django.core.exceptions import ValidationError
from django.db.models import Q

from datamesh.models import Relationship, JoinRecord, LogicModuleModel
from gateway.utils import valid_uuid4


def prepare_lookup_kwargs(is_forward_lookup: bool,
                          relationship: Relationship,
                          join_record: JoinRecord) -> Tuple[LogicModuleModel, str]:
    """Find out if pk is id or uuid and prepare lookup according to direction."""
    if is_forward_lookup:
        related_model = relationship.related_model
        related_record_field = 'related_record_id' if join_record.related_record_id is not None \
            else 'related_record_uuid'
    else:
        related_model = relationship.origin_model
        related_record_field = 'record_id' if join_record.record_id is not None \
            else 'record_uuid'

    return related_model, related_record_field


def validate_join(origin_model_pk: [str, int], related_model_pk: [str, int], relationship: str):
    """This function is validating the join if the join not created, yet then it will create the join """
    pk_dict = validate_primary_key(origin_model_pk=origin_model_pk, related_model_pk=related_model_pk)

    join_record_instance = JoinRecord.objects.filter(**pk_dict, relationship__key=relationship)
    if not join_record_instance:
        return join_record(pk_dict=pk_dict, relationship=relationship, origin_model_pk=None, related_model_pk=None)


def join_record(relationship: str, origin_model_pk: [str, int], related_model_pk: [str, int], pk_dict: [dict, None]):
    """This function will create datamesh join"""

    # validate primary key combination and pass it ro create function
    if not pk_dict:
        pk_dict = validate_primary_key(origin_model_pk=origin_model_pk, related_model_pk=related_model_pk)

    try:
        JoinRecord.objects.create(
            relationship=Relationship.objects.filter(key=relationship).first(),
            **pk_dict,
            organization_id=None
        )
        return True
    except ValidationError:
        return False


def delete_join_record(pk: [str, int], previous_pk: [str, int]):
    """
    This function will delete
    1.join associated with particulate primary key.
    2.if relation have both origin_model_pk and related_model_pk then it deletes this single join
    """

    # retrieve the related join associated with pk
    pk_query_set = JoinRecord.objects.filter(Q(record_uuid__icontains=pk) | Q(related_record_uuid__icontains=pk)
                                             | Q(record_id__icontains=pk) | Q(related_record_id__icontains=pk))

    # if relation have previous_pk then filter in pk_query_set and delete the join
    if previous_pk and pk:
        pk_dict = validate_primary_key(origin_model_pk=pk, related_model_pk=previous_pk)
        pk_query_set.filter(**pk_dict).delete()

        pk_dict = validate_primary_key(origin_model_pk=previous_pk, related_model_pk=pk)
        pk_query_set.filter(**pk_dict).delete()
        return True

    # if not then delete join entry associated with pk
    if pk and not previous_pk:
        return pk_query_set.delete()


def validate_primary_key(origin_model_pk: [str, int], related_model_pk: [str, int]):
    origin_pk_type = 'uuid' if valid_uuid4(str(origin_model_pk)) else 'id'
    related_pk_type = 'uuid' if valid_uuid4(str(related_model_pk)) else 'id'

    if origin_pk_type == 'id' and related_pk_type == 'id':
        return {
            "record_id": origin_model_pk,
            "related_record_id": related_model_pk
        }

    elif origin_pk_type == 'uuid' and related_pk_type == 'uuid':
        return {
            "record_uuid": origin_model_pk,
            "related_record_uuid": related_model_pk
        }

    elif origin_pk_type == 'uuid' and related_pk_type == 'id':
        return {
            "record_uuid": origin_model_pk,
            "related_record_id": related_model_pk
        }

    elif origin_pk_type == 'id' and related_pk_type == 'uuid':
        return {
            "record_id": origin_model_pk,
            "related_record_uuid": related_model_pk
        }


def prepare_request(request: any, request_param: dict, related_model_pk: [int, str]):
    """This function will create datamesh URL to get individual objects from particulate service"""

    meta_data, service_url = request.META, None
    request_host = f'{meta_data["wsgi.url_scheme"]}://{meta_data["HTTP_HOST"]}'

    # If the relation is local than it doesn't have service parameter
    if not request_param['is_local']:
        path = f'/{request_param["service"]}/{request_param["model"]}/{related_model_pk}/'
    else:
        path = f'/{request_param["model"]}/{related_model_pk}/'

    service_url = f'{request_host}{path}'
    header = {'Authorization': meta_data["HTTP_AUTHORIZATION"]}

    return service_url, header
