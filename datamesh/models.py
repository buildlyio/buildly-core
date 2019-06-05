import uuid

from django.db import models
from django.db.models import CheckConstraint, Q

from gateway.models import LogicModule
from workflow.models import Organization


class LogicModuleModel(models.Model):
    logic_module_model_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    logic_module = models.ForeignKey(LogicModule, related_name='models', on_delete=models.CASCADE)
    model = models.CharField(max_length=128)
    endpoint = models.CharField(max_length=255, blank=True, help_text="Endpoint of the model")

    class Meta:
        unique_together = (
            'logic_module', 
            'model', 
        )

    def __str__(self):
        return f'{self.logic_module} - {self.model}'


class Relationship(models.Model):
    relationship_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    origin_model = models.ForeignKey(LogicModuleModel, related_name='joins_origins', on_delete=models.CASCADE)
    related_model = models.ForeignKey(LogicModuleModel, related_name='joins_relateds', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.origin_model} -> {self.related_model}'
    
    class Meta:
        unique_together = (
            'relationship_uuid',
            'origin_model',
            'related_model',
        )


class JoinRecord(models.Model):
    join_records_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    relationship = models.ForeignKey(Relationship, related_name='joinrecords', on_delete=models.CASCADE)
    record_id = models.PositiveIntegerField(blank=True, null=True)
    record_uuid = models.UUIDField(blank=True, null=True)
    related_record_id = models.PositiveIntegerField(blank=True, null=True)
    related_record_uuid = models.UUIDField(blank=True, null=True)
    organization = models.ForeignKey(Organization, null=True, blank=True, help_text="Related Organization with access", on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            'relationship',
            'record_id',
            'record_uuid',
            'related_record_id',
            'related_record_uuid',
            'organization',
        )
        constraints = [
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
