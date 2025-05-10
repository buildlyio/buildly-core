import random
import string
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField

from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone

import requests
import logging


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
    description = models.TextField(
        "Description/Notes", max_length=765, null=True, blank=True
    )
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


class OrganizationType(models.Model):
    """
    Allows organization to be of multiple types.
    """
    name = models.CharField("Name", max_length=255, blank=True, help_text="Organization type")
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Organization Types"

    def save(self, *args, **kwargs):
        if self.create_date is None:
            self.create_date = timezone.now()
        self.edit_date = timezone.now()
        super(OrganizationType, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class Organization(models.Model):
    """
    The organization instance. There could be multiple organizations inside one application.
    When organization is created two CoreGroups are created automatically: Admins group and default Users group.
    """

    organization_uuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name='Organization UUID'
    )
    name = models.CharField(
        "Organization Name",
        max_length=255,
        blank=True,
        help_text="Each end user must be grouped into an organization",
    )
    description = models.TextField(
        "Description/Notes",
        max_length=765,
        null=True,
        blank=True,
        help_text="Description of organization",
    )
    organization_url = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="Link to organizations external web site",
    )
    industries = models.ManyToManyField(
        Industry,
        blank=True,
        related_name='organizations',
        help_text="Type of Industry the organization belongs to if any",
    )
    create_date = models.DateTimeField(null=True, blank=True)
    edit_date = models.DateTimeField(null=True, blank=True)
    oauth_domains = models.CharField("OAuth Domains", max_length=255, null=True, blank=True)

    date_format = models.CharField(
        "Date Format", max_length=50, blank=True, default="DD.MM.YYYY"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    allow_import_export = models.BooleanField('To allow import export functionality', default=False)
    radius = models.FloatField(max_length=20, blank=True, null=True, default=0.0)
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.CASCADE, null=True)
    stripe_subscription_details = JSONField(blank=True, null=True)
    unlimited_free_plan = models.BooleanField('Free unlimited features plan', default=True)
    coupon = models.ForeignKey('core.Coupon', on_delete=models.SET_NULL, blank=True, null=True)

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
            permissions=PERMISSIONS_ORG_ADMIN,
        )

        CoreGroup.objects.create(
            organization=self,
            is_org_level=True,
            is_default=True,
            name='Users',
            permissions=PERMISSIONS_VIEW_ONLY,
        )


class Referral(models.Model):
    referral_uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name='organization_referrals')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    link= models.TextField(unique=True, null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    max_usage = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)
    coupon = models.ForeignKey('core.Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.code = f"INSIGHTS-REF-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            self.link = f'{settings.FRONTEND_URL}{settings.REGISTRATION_URL_PATH}?referral_code={self.code}'
        super(Referral, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.code}-{self.name}'


class CoreGroup(models.Model):
    """
    CoreGroup model defines the groups of the users with specific permissions 
    """

    uuid = models.CharField(
        'CoreGroup UUID', max_length=255, default=uuid.uuid4, unique=True
    )
    name = models.CharField('Name of the role', max_length=80)
    organization = models.ForeignKey(Organization, blank=True, null=True, on_delete=models.CASCADE,
                                     help_text='Related Org to associate with')
    is_global = models.BooleanField('Is global group', default=False)
    is_org_level = models.BooleanField('Is organization level group', default=False)
    is_default = models.BooleanField('Is organization default group', default=False)
    permissions = models.PositiveSmallIntegerField('Permissions', default=PERMISSIONS_VIEW_ONLY,
                                                   help_text='Decimal integer from 0 to 15 converted from 4-bit binary, each bit indicates permissions for CRUD')
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

    TITLE_CHOICES = (('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'))

    core_user_uuid = models.CharField(
        max_length=255, verbose_name='CoreUser UUID', default=uuid.uuid4, unique=True
    )
    USER_TYPE_CHOICES = (
        ('Developer', 'Developer'),
        ('Product Team', 'Product Team'),
    )

    USER_TYPE_CHOICES = (
        ('Developer', 'Developer'),
        ('Product Team', 'Product Team'),
    )

    USER_TYPE_CHOICES = (
        ('Developer', 'Developer'),
        ('Product Team', 'Product Team'),
    )

    core_user_uuid = models.CharField(max_length=255, verbose_name='CoreUser UUID', default=uuid.uuid4, unique=True)
    title = models.CharField(blank=True, null=True, max_length=3, choices=TITLE_CHOICES)
    contact_info = models.CharField(blank=True, null=True, max_length=255)
    organization = models.ForeignKey(
        Organization,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text='Related Org to associate with',
    )
    core_groups = models.ManyToManyField(
        CoreGroup,
        verbose_name='User groups',
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )
    privacy_disclaimer_accepted = models.BooleanField(default=False)
    tos_disclaimer_accepted = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)
    edit_date = models.DateTimeField(null=True, blank=True)
    email_preferences = JSONField(blank=True, null=True)
    push_preferences = JSONField(blank=True, null=True)
    user_timezone = models.CharField(blank=True, null=True, max_length=255)
    survey_status = models.BooleanField(default=False)
    user_type = models.CharField(blank=True, null=True, max_length=50, choices=USER_TYPE_CHOICES, default='Product Team')
    survey_status = models.BooleanField(default=False)
    coupon_code = models.CharField(max_length=48, blank=True, null=True)

    REQUIRED_FIELDS = []

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
            # Send user details to HubSpot
            try:
                self.send_to_hubspot()
            except requests.RequestException as e:
                # Log the error
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send user details to HubSpot: {e}")

    def send_to_hubspot(self):
        url = "https://api.hubapi.com/contacts/v1/contact"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}"
        }
        data = {
            "properties": [
                {"property": "email", "value": self.email},
                {"property": "firstname", "value": self.first_name},
                {"property": "lastname", "value": self.last_name},
                {"property": "company", "value": self.organization.name if self.organization else ""},
                {"property": "jobtitle", "value": self.title},
                {"property": "user_type", "value": self.user_type},
            ]
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

    @property
    def is_org_admin(self) -> bool:
        """
        Check if user has organization level admin permissions
        """
        if not hasattr(self, '_is_org_admin'):
            self._is_org_admin = self.core_groups.filter(
                permissions=PERMISSIONS_ORG_ADMIN, is_org_level=True
            ).exists()
        return self._is_org_admin

    @property
    def is_global_admin(self) -> bool:
        """
        Check if user has organization level admin permissions
        """
        if self.is_superuser:
            return True
        if not hasattr(self, '_is_global_admin'):
            self._is_global_admin = self.core_groups.filter(
                permissions=PERMISSIONS_ADMIN, is_global=True
            ).exists()
        return self._is_global_admin


class EmailTemplate(models.Model):
    """
    Stores e-mail templates specific to organization
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='Organization',
                                     help_text='Related Org to associate with')
    subject = models.CharField('Subject', max_length=255)
    type = models.PositiveSmallIntegerField('Type of template', choices=TEMPLATE_TYPES)
    template = models.TextField(
        "Reset password e-mail template (text)", null=True, blank=True
    )
    template_html = models.TextField(
        "Reset password e-mail template (HTML)", null=True, blank=True
    )

    class Meta:
        unique_together = ('organization', 'type',)
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f'{self.type} ({self.organization})'


class LogicModule(models.Model):
    module_uuid = models.CharField(
        max_length=255,
        verbose_name='Logic Module UUID',
        default=uuid.uuid4,
        unique=True,
    )
    name = models.CharField("Logic Module Name", max_length=255, blank=True)
    description = models.TextField(
        "Description/Notes", max_length=765, null=True, blank=True
    )
    endpoint = models.CharField(blank=True, null=True, max_length=255)
    endpoint_name = models.CharField(blank=True, null=True, max_length=255)
    docs_endpoint = models.CharField(blank=True, null=True, max_length=255)
    api_specification = JSONField(blank=True, null=True)
    swagger_version = models.CharField(max_length=50, null=True, blank=True)
    core_groups = models.ManyToManyField(
        CoreGroup,
        verbose_name='Logic Module groups',
        blank=True,
        related_name='logic_module_set',
        related_query_name='logic_module',
    )

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


class Coupon(models.Model):
    FOREVER = 'forever'
    ONCE = 'once'
    REPEATING = 'repeating'

    DurationChoices = (
        (FOREVER, 'Forever'),
        (ONCE, 'Once'),
        (REPEATING, 'Repeating'),
    )

    coupon_uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=24, unique=True, blank=True, null=True)
    duration = models.CharField(choices=DurationChoices, max_length=16, default=ONCE)
    duration_in_months = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)  # maps to valid field on stripe
    max_redemptions = models.IntegerField(default=1)
    percent_off = models.FloatField(default=0)
    amount_off = models.FloatField(default=0)
    discount_amount = models.FloatField(default=0)
    currency = models.CharField(max_length=3, default='usd')
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    stripe_coupon_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f'{self.code}-{self.name}'

    def generate_code(self):
        # generate code (First  letters INSIGHTS + 6 random digits (letters and numbers)
        self.code = f"INSIGHTS-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        self.save()


class Subscription(models.Model):
    subscription_uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    stripe_subscription_id = models.CharField(max_length=255, null=True)
    stripe_product = models.CharField(max_length=255)
    stripe_product_info = models.JSONField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255, null=True)
    stripe_payment_method_id = models.CharField(max_length=255, null=True, blank=True)
    trial_start_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        'core.CoreUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='user_subscription'
    )
    created_by = models.ForeignKey(
        'core.CoreUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='created_subscription'
    )
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='organization_subscription'
    )
    cancelled = models.BooleanField(default=False)
    cancelled_date = models.DateTimeField(null=True, blank=True)
    coupon = models.ForeignKey(
        'core.Coupon',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='coupon_subscription'
    )

    def __str__(self):
        return self.stripe_subscription_id

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ['-create_date']
