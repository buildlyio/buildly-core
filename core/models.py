import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone

ROLE_ORGANIZATION_ADMIN = 'OrgAdmin'
ROLE_WORKFLOW_ADMIN = 'WorkflowAdmin'
ROLE_WORKFLOW_TEAM = 'WorkflowTeam'
ROLE_VIEW_ONLY = 'ViewOnly'
ROLES = (
    (ROLE_ORGANIZATION_ADMIN, ROLE_ORGANIZATION_ADMIN),
    (ROLE_WORKFLOW_ADMIN, ROLE_WORKFLOW_ADMIN),
    (ROLE_WORKFLOW_TEAM, ROLE_WORKFLOW_TEAM),
    (ROLE_VIEW_ONLY, ROLE_VIEW_ONLY),
)

PERMISSIONS_ORG_ADMIN = 15  # 1111

PERMISSIONS_ADMIN = PERMISSIONS_ORG_ADMIN

PERMISSIONS_WORKFLOW_ADMIN = PERMISSIONS_ORG_ADMIN

PERMISSIONS_WORKFLOW_TEAM = 14  # 1110

PERMISSIONS_VIEW_ONLY = 4  # 0100

PERMISSIONS_NO_ACCESS = 0  # 0000

TEMPLATE_RESET_PASSWORD, TEMPLATE_INVITE = 1, 2
TEMPLATE_TYPES = (
    (TEMPLATE_RESET_PASSWORD, 'Password resetting'),
    (TEMPLATE_INVITE, 'Invitation'),
)


class CoreSites(models.Model):
    name = models.CharField(blank=True, null=True, max_length=255)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    privacy_disclaimer = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now=False, blank=True, null=True)
    updated = models.DateTimeField(auto_now=False, blank=True, null=True)
    whitelisted_domains = models.TextField("Whitelisted Domains", null=True, blank=True)

    class Meta:
        verbose_name = "Core Site"
        verbose_name_plural = "Core Sites"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if kwargs.pop('new_entry', True):
            self.created = timezone.now()
        else:
            self.updated = timezone.now()
        return super(CoreSites, self).save(*args, **kwargs)


class Industry(models.Model):
    name = models.CharField("Industry Name", max_length=255, blank=True, default="Tech")
    description = models.TextField("Description/Notes", max_length=765, null=True, blank=True)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Industries"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Industry, self).save()

    def __str__(self):
        return self.name


class Organization(models.Model):
    """
    The organization instance. There could be multiple organizations inside one application.
    When organization is created two CoreGroups are created automatically: Admins group and default Users group.
    """
    organization_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='Organization UUID')
    name = models.CharField("Organization Name", max_length=255, blank=True, help_text="Each end user must be grouped into an organization")
    description = models.TextField("Description/Notes", max_length=765, null=True, blank=True, help_text="Description of organization")
    organization_url = models.CharField(blank=True, null=True, max_length=255, help_text="Link to organizations external web site")
    industries = models.ManyToManyField(Industry, blank=True, related_name='organizations', help_text="Type of Industry the organization belongs to if any")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    oauth_domains = ArrayField(models.CharField("OAuth Domains", max_length=255, null=True, blank=True), null=True, blank=True)
    date_format = models.CharField("Date Format", max_length=50, blank=True, default="DD.MM.YYYY")
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Organizations"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(Organization, self).save()
        if is_new:
            self._create_initial_groups()

    def _create_initial_groups(self):
        CoreGroup.objects.create(
            organization=self,
            is_org_level=True,
            name='Admins',
            permissions=PERMISSIONS_ORG_ADMIN
        )

        CoreGroup.objects.create(
            organization=self,
            is_org_level=True,
            is_default=True,
            name='Users',
            permissions=PERMISSIONS_VIEW_ONLY
        )


class CoreGroup(models.Model):
    """
    CoreGroup model defines the groups of the users with specific permissions for the set of workflowlevel1's
    and workflowlevel2's (it has many-to-many relationship to WorkFlowLevel1 and WorkFlowLevel2 models).
    Permissions field is the decimal integer from 0 to 15 converted from 4-bit binary, each bit indicates permissions
    for CRUD. For example: 12 -> 1100 -> CR__ (allowed to Create and Read).
    """
    uuid = models.CharField('CoreGroup UUID', max_length=255, default=uuid.uuid4, unique=True)
    name = models.CharField('Name of the role', max_length=80)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE, help_text='Related Org to associate with')
    is_global = models.BooleanField('Is global group', default=False)
    is_org_level = models.BooleanField('Is organization level group', default=False)
    is_default = models.BooleanField('Is organization default group', default=False)
    permissions = models.PositiveSmallIntegerField('Permissions', default=PERMISSIONS_VIEW_ONLY, help_text='Decimal integer from 0 to 15 converted from 4-bit binary, each bit indicates permissions for CRUD')
    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} <{self.organization}>'

    def save(self, *args, **kwargs):
        self.edit_date = timezone.now()
        super(CoreGroup, self).save(*args, **kwargs)

    @property
    def display_permissions(self) -> str:
        return '{0:04b}'.format(self.permissions if self.permissions < 16 else 15)


class CoreUser(AbstractUser):
    """
    CoreUser is the registered user who belongs to some organization and can manage its projects.
    """
    TITLE_CHOICES = (
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
    )

    USER_TYPE_CHOICES = (
        ('Developer', 'Developer'),
        ('Product Team', 'Product Team'),
    )

    core_user_uuid = models.CharField(max_length=255, verbose_name='CoreUser UUID', default=uuid.uuid4, unique=True)
    title = models.CharField(blank=True, null=True, max_length=3, choices=TITLE_CHOICES)
    contact_info = models.CharField(blank=True, null=True, max_length=255)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE, help_text='Related Org to associate with')
    core_groups = models.ManyToManyField(CoreGroup, verbose_name='User groups', blank=True, related_name='user_set', related_query_name='user')
    privacy_disclaimer_accepted = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(blank=True, null=True, max_length=50, choices=USER_TYPE_CHOICES)
    survey_status = models.BooleanField(default=False)

    class Meta:
        ordering = ('first_name',)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(CoreUser, self).save()
        if is_new:
            # Add default groups
            self.core_groups.add(*CoreGroup.objects.filter(organization=self.organization, is_default=True))

    @property
    def is_org_admin(self) -> bool:
        """
        Check if user has organization level admin permissions
        """
        if not hasattr(self, '_is_org_admin'):
            self._is_org_admin = self.core_groups.filter(permissions=PERMISSIONS_ORG_ADMIN, is_org_level=True).exists()
        return self._is_org_admin

    @property
    def is_global_admin(self) -> bool:
        """
        Check if user has organization level admin permissions
        """
        if self.is_superuser:
            return True
        if not hasattr(self, '_is_global_admin'):
            self._is_global_admin = self.core_groups.filter(permissions=PERMISSIONS_ADMIN, is_global=True).exists()
        return self._is_global_admin


class EmailTemplate(models.Model):
    """
    Stores e-mail templates specific to organization
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='Organization', help_text='Related Org to associate with')
    subject = models.CharField('Subject', max_length=255)
    type = models.PositiveSmallIntegerField('Type of template', choices=TEMPLATE_TYPES)
    template = models.TextField("Reset password e-mail template (text)", null=True, blank=True)
    template_html = models.TextField("Reset password e-mail template (HTML)", null=True, blank=True)

    class Meta:
        unique_together = ('organization', 'type',)
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f'{self.type} ({self.organization})'


class LogicModule(models.Model):
    module_uuid = models.CharField(max_length=255, verbose_name='Logic Module UUID', default=uuid.uuid4, unique=True)
    name = models.CharField("Logic Module Name", max_length=255, blank=True)
    description = models.TextField("Description/Notes", max_length=765, null=True, blank=True)
    endpoint = models.CharField(blank=True, null=True, max_length=255)
    endpoint_name = models.CharField(blank=True, null=True, max_length=255)
    docs_endpoint = models.CharField(blank=True, null=True, max_length=255)
    api_specification = JSONField(blank=True, null=True)
    core_groups = models.ManyToManyField(CoreGroup, verbose_name='Logic Module groups', blank=True, related_name='logic_module_set', related_query_name='logic_module')
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Logic Modules"
        unique_together = (('endpoint', 'endpoint_name'),)

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(LogicModule, self).save()

    def __str__(self):
        return str(self.name)


class Partner(models.Model):
    partner_uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, null=True, max_length=255)
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
