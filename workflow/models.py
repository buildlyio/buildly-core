import uuid
from typing import Union

from django.db import models
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

from core.models import CoreUser, CoreGroup, Organization, ROLE_ORGANIZATION_ADMIN

DEFAULT_PROGRAM_NAME = 'Default program'


class Internationalization(models.Model):
    language = models.CharField("Language", blank=True, null=True, max_length=100)
    language_file = JSONField()
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('language',)

    def __str__(self):
        return self.language

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Internationalization, self).save()


class WorkflowLevelType(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField("Name", max_length=255, help_text="Name of workflow2 type")
    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('create_date',)


class WorkflowLevelStatus(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.PositiveSmallIntegerField(default=0)
    name = models.CharField(
        "Name", max_length=255, help_text="Name of WorkflowLevelStatus"
    )
    short_name = models.SlugField(max_length=63, unique=True)
    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('order',)
        verbose_name = "Workflow Level Status"
        verbose_name_plural = "Workflow Level Statuses"


class WorkflowLevel1(models.Model):
    level1_uuid = models.CharField(
        max_length=255,
        editable=False,
        verbose_name='WorkflowLevel1 UUID',
        default=uuid.uuid4,
        unique=True,
    )
    unique_id = models.CharField(
        "ID",
        max_length=255,
        blank=True,
        null=True,
        help_text="User facing unique ID field if needed",
    )
    name = models.CharField(
        "Name",
        max_length=255,
        blank=True,
        help_text="Top level workflow can have child workflowleves, name it according to it's grouping of children",
    )
    organization = models.ForeignKey(
        Organization,
        blank=True,
        on_delete=models.CASCADE,
        null=True,
        help_text='Related Org to associate with',
    )
    description = models.TextField(
        "Description",
        max_length=765,
        null=True,
        blank=True,
        help_text='Describe how this collection of related workflows are used',
    )
    user_access = models.ManyToManyField(CoreUser, blank=True)
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='If required a time span can be associated with workflow level',
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='If required a time span can be associated with workflow level',
    )
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    sort = models.IntegerField(default=0)  # sort array
    core_groups = models.ManyToManyField(
        CoreGroup,
        verbose_name='Core groups',
        blank=True,
        related_name='workflowlevel1s',
        related_query_name='workflowlevel1s',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Workflow Level 1"
        verbose_name_plural = "Workflow Level 1"

    def save(self, *args, **kwargs):
        if not 'force_insert' in kwargs:
            kwargs['force_insert'] = False
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()

        super(WorkflowLevel1, self).save()

    def delete(self, *args, **kwargs):
        super(WorkflowLevel1, self).delete(*args, **kwargs)

    def __str__(self):
        if self.organization:
            return f'{self.name} <{self.organization.name}>'
        else:
            return self.name


class WorkflowLevel2(models.Model):
    level2_uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name='WorkflowLevel2 UUID',
        help_text="Unique ID",
    )
    description = models.TextField(
        "Description",
        blank=True,
        null=True,
        help_text="Description of the workflow level use",
    )
    name = models.CharField(
        "Name",
        max_length=255,
        help_text="Name of workflow level as it relates to workflow level 1",
    )
    notes = models.TextField(blank=True, null=True)
    parent_workflowlevel2 = models.IntegerField(
        "Parent",
        default=0,
        blank=True,
        help_text="Workflow level 2 can relate to another workflow level 2 creating multiple levels of relationships",
    )
    short_name = models.CharField(
        "Code",
        max_length=20,
        blank=True,
        null=True,
        help_text="Shortened name autogenerated",
    )
    workflowlevel1 = models.ForeignKey(
        WorkflowLevel1,
        verbose_name="Workflow Level 1",
        on_delete=models.CASCADE,
        related_name="workflowlevel2",
        help_text="Primary or parent Workflow",
    )
    create_date = models.DateTimeField("Date Created", null=True, blank=True)
    created_by = models.ForeignKey(
        CoreUser,
        related_name='workflowlevel2',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    edit_date = models.DateTimeField("Last Edit Date", null=True, blank=True)
    core_groups = models.ManyToManyField(
        CoreGroup,
        verbose_name='Core groups',
        blank=True,
        related_name='workflowlevel2s',
        related_query_name='workflowlevel2s',
    )
    start_date = models.DateTimeField("Start Date", null=True, blank=True)
    end_date = models.DateTimeField("End Date", null=True, blank=True)
    type = models.ForeignKey(
        WorkflowLevelType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='workflowlevel2s',
    )
    status = models.ForeignKey(
        WorkflowLevelStatus,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='workflowlevel2s',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Workflow Level 2"
        verbose_name_plural = "Workflow Level 2"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()

        super(WorkflowLevel2, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def organization(self) -> Union[Organization, None]:
        return self.workflowlevel1.organization


class WorkflowTeam(models.Model):
    """
    WorkflowTeam defines m2m relations between CoreUser and Workflowlevel1.
    It also defines a role for this relationship (as a fk to Group instance).
    """

    team_uuid = models.CharField(
        max_length=255,
        editable=False,
        verbose_name='WorkflowLevel1 UUID',
        default=uuid.uuid4,
        unique=True,
    )
    workflow_user = models.ForeignKey(
        CoreUser,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="auth_approving",
        help_text='User with access/permissions to related workflowlevels',
    )
    workflowlevel1 = models.ForeignKey(
        WorkflowLevel1,
        null=True,
        on_delete=models.CASCADE,
        blank=True,
        help_text='Related workflowlevel 1',
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='If required a time span can be associated with workflow level access',
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='If required a time span can be associated with workflow level access expiration',
    )
    status = models.CharField(
        max_length=255, null=True, blank=True, help_text='Active status of access'
    )
    role = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text='Type of access via related group',
    )
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('workflow_user',)
        verbose_name = "Workflow Team"
        verbose_name_plural = "Workflow Teams"

    def clean(self):
        if self.role and self.role.name == ROLE_ORGANIZATION_ADMIN:
            raise ValidationError(
                'Workflowteam role can not be ROLE_ORGANIZATION_ADMIN'
            )

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(WorkflowTeam, self).save()

    def __str__(self):
        return f'{self.workflow_user} - {self.role} <{self.workflowlevel1}>'

    @property
    def organization(self) -> Union[Organization, None]:
        return self.workflowlevel1.organization if self.workflowlevel1 else None


class WorkflowLevel2Sort(models.Model):
    workflowlevel1 = models.ForeignKey(
        WorkflowLevel1, null=True, on_delete=models.CASCADE, blank=True
    )
    workflowlevel2_parent = models.ForeignKey(
        WorkflowLevel2, on_delete=models.CASCADE, null=True, blank=True
    )
    workflowlevel2_pk = models.UUIDField(
        "UUID to be Sorted", default='00000000-0000-4000-8000-000000000000'
    )
    sort_array = JSONField(
        null=True, blank=True, help_text="Sorted JSON array of workflow levels"
    )
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('workflowlevel1', 'workflowlevel2_pk')
        verbose_name = "Workflow Level Sort"
        verbose_name_plural = "Workflow Level Sort"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(WorkflowLevel2Sort, self).save()

    def __str__(self):
        return self.workflowlevel1

    @property
    def organization(self) -> Union[Organization, None]:
        return self.workflowlevel1.organization if self.workflowlevel1 else None
