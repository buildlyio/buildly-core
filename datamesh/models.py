import uuid
from typing import Tuple, List

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint

from core.models import Organization
from datamesh.managers import JoinRecordManager, LogicModuleModelManager


class LogicModuleModel(models.Model):
    logic_module_model_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logic_module_endpoint_name = models.CharField(max_length=255, help_text="Without leading and trailing slashes")
    model = models.CharField(max_length=128)
    endpoint = models.CharField(max_length=255, help_text="Endpoint of the model with leading and trailing slashs, p.e.: '/siteprofiles/'")
    lookup_field_name = models.SlugField(max_length=64, default='id', help_text="Name of the field in the model for detail methods, p.e.: 'id' or 'uuid'")
    is_local = models.BooleanField(default=False, help_text="Local model is taken from Buildly")

    objects = LogicModuleModelManager()

    class Meta:
        unique_together = (
            ('logic_module_endpoint_name', 'model'),
            ('logic_module_endpoint_name', 'endpoint')
        )

    def __str__(self):
        return f'{self.logic_module_endpoint_name} - {self.model} - /{self.logic_module_endpoint_name}{self.endpoint}'

    def get_relationships(self) -> List[Tuple[models.Model, bool]]:
        """
        Get relationships with direction.
        :param self: The Logic Module Model for the relations
        :return list: list of tuples with relationship and \
            boolean for forward or reverse direction (True = forwards, False = backwards)
        """
        relationships = Relationship.objects.filter(
            Q(origin_model=self) | Q(related_model=self)
        )
        relationships_with_direction = list()
        for relationship in relationships:
            relationships_with_direction.append((relationship,
                                                 relationship.origin_model == self))

        return relationships_with_direction

    @property
    def concatenated_model_name(self) -> str:
        return self.logic_module_endpoint_name + self.model

    def save(self, **kwargs):
        self.logic_module_endpoint_name = self.logic_module_endpoint_name.strip('/')
        super().save(**kwargs)


class Relationship(models.Model):
    key = models.SlugField(max_length=64, help_text="The key in the response body, where the related object data will be saved into, p.e.: 'contact_siteprofile_relationship'.")
    relationship_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin_model = models.ForeignKey(LogicModuleModel, related_name='joins_origins', on_delete=models.CASCADE)
    related_model = models.ForeignKey(LogicModuleModel, related_name='joins_relateds', on_delete=models.CASCADE)
    fk_field_name = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f'{self.origin_model} -> {self.related_model}'

    def validate_reverse_relationship_absence(self):
        """Validate reverse relationship does not exist already."""
        if self.__class__.objects.filter(origin_model=self.related_model, related_model=self.origin_model).count():
            raise ValidationError("Reverse relationship already exists.")

    def save(self, *args, **kwargs):
        self.validate_reverse_relationship_absence()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            'relationship_uuid',
            'origin_model',
            'related_model',
        )


class JoinRecord(models.Model):
    join_record_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relationship = models.ForeignKey(Relationship, related_name='joinrecords', on_delete=models.CASCADE)
    record_id = models.PositiveIntegerField(blank=True, null=True)
    record_uuid = models.UUIDField(blank=True, null=True)
    related_record_id = models.PositiveIntegerField(blank=True, null=True)
    related_record_uuid = models.UUIDField(blank=True, null=True)
    organization = models.ForeignKey(Organization, null=True, blank=True, help_text="Related Organization with access", on_delete=models.CASCADE)

    objects = JoinRecordManager()

    class Meta:
        # 4 UniqueConstraints for unique_together for 'relationship','organization',
        # 'record_id', 'record_uuid', 'related_record_id', 'related_record_uuid'
        constraints = [
            UniqueConstraint(
                fields=(
                    'relationship',
                    'record_id',
                    'related_record_id',
                ),
                name='unique_join_record_ids',
                condition=Q(record_uuid=None, related_record_uuid=None)
            ),
            UniqueConstraint(
                fields=(
                    'relationship',
                    'record_uuid',
                    'related_record_uuid',
                ),
                name='unique_join_record_uuids',
                condition=Q(record_id=None, related_record_id=None)
            ),
            UniqueConstraint(
                fields=(
                    'relationship',
                    'record_id',
                    'related_record_uuid',
                ),
                name='unique_join_record_id_uuid',
                condition=Q(record_uuid=None, related_record_id=None)
            ),
            UniqueConstraint(
                fields=(
                    'relationship',
                    'record_uuid',
                    'related_record_id',
                ),
                name='unique_join_record_uuid_id',
                condition=Q(record_id=None, related_record_uuid=None)
            ),
            CheckConstraint(
                name='one_record_primary_key',
                check=~Q(record_id=None, record_uuid=None) & (~(~Q(record_id=None) & ~Q(record_uuid=None)))
            ),
            CheckConstraint(
                name='one_related_record_primary_key',
                check=~Q(related_record_id=None, related_record_uuid=None) & (
                    ~(~Q(related_record_id=None) & ~Q(related_record_uuid=None)))
            ),
        ]

    def __str__(self):
        return f'{self.relationship} - ' \
            f'{self.record_id or self.record_uuid} -> {self.related_record_id or self.related_record_uuid}'
