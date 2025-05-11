import jwt
import secrets
from urllib.parse import urljoin

from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import Template, Context

from rest_framework import serializers

from oauth2_provider.models import AccessToken, Application, RefreshToken

from core.email_utils import send_email, send_email_body
from core.helpers.oauth import EmailVerificationToken

from core.models import CoreUser, CoreGroup, EmailTemplate, LogicModule, Organization, OrganizationType, PERMISSIONS_ORG_ADMIN, \
    TEMPLATE_RESET_PASSWORD, PERMISSIONS_VIEW_ONLY, Partner, Subscription, Coupon, Referral, ROLE_ORGANIZATION_ADMIN


class LogicModuleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    uuid = serializers.ReadOnlyField()

    class Meta:
        model = LogicModule
        fields = '__all__'


class PermissionsField(serializers.DictField):
    """
    Field for representing int-value permissions as a JSON object in the format.
    For example:
    9 -> '1001' (binary representation) -> `{'create': True, 'read': False, 'update': False, 'delete': True}`
    """
    _keys = ('create', 'read', 'update', 'delete')

    def __init__(self, *args, **kwargs):
        kwargs['child'] = serializers.BooleanField()
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        permissions = list('{0:04b}'.format(value if value < 16 else 15))
        return dict(zip(self._keys, map(bool, map(int, permissions))))

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        keys = data.keys()
        if not set(keys) == set(self._keys):
            raise serializers.ValidationError("Permissions field: incorrect keys format")

        permissions = ''.join([str(int(data[key])) for key in self._keys])
        return int(permissions, 2)


class UUIDPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return str(super().to_representation(value))


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='organization_uuid', read_only=True)
    subscriptions = serializers.SerializerMethodField()
    subscription_active = serializers.SerializerMethodField()
    referral_link = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = '__all__'

    def get_subscriptions(self, organization):
        # check if user is OrgAdmin
        if self.context.get('request') and hasattr(self.context.get('request'), 'user'):
            try:
                user_groups = self.context.get('request').user.core_groups.values_list('name', flat=True)
            except AttributeError:
                user_groups = []
            if 'Admins' in user_groups:
                return SubscriptionSerializer(
                    organization.organization_subscription.all(),
                    many=True
                ).data
        return []

    def get_subscription_active(self, organization):
        return organization.organization_subscription.filter(
            subscription_end_date__gte=timezone.now().date()
        ).exists()

    def get_referral_link(self, organization):
        if organization.organization_referrals.exists():
            return organization.organization_referrals.first().link
        return None


class CoreGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionsField(required=False)
    organization = UUIDPrimaryKeyRelatedField(
        required=False,
        queryset=Organization.objects.all(),
        help_text="Related Org to associate with"
    )

    class Meta:
        model = CoreGroup
        read_only_fields = ('uuid',)
        fields = (
            'id', 'uuid',
            'name',
            'is_global',
            'is_org_level',
            'permissions',
            'organization',
        )


class CoreUserSerializer(serializers.ModelSerializer):
    """
    Default CoreUser serializer
    """
    is_active = serializers.BooleanField(required=False)
    core_groups = CoreGroupSerializer(read_only=True, many=True)
    invitation_token = serializers.CharField(required=False)
    organization = OrganizationSerializer(read_only=True)
    subscription_active = serializers.SerializerMethodField()

    def validate_invitation_token(self, value):
        try:
            decoded = jwt.decode(value, settings.SECRET_KEY, algorithms='HS256')
            coreuser_exists = CoreUser.objects.filter(email=decoded['email']).exists()
            if coreuser_exists or decoded['email'] != self.initial_data['email']:
                raise serializers.ValidationError('Token is not valid.')
        except jwt.DecodeError:
            raise serializers.ValidationError('Token is not valid.')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Token is expired.')
        return value

    class Meta:
        model = CoreUser
        fields = ('id', 'core_user_uuid', 'first_name', 'last_name', 'email', 'username', 'is_active',
                  'title', 'contact_info', 'privacy_disclaimer_accepted','tos_disclaimer_accepted', 'organization', 'core_groups',
                  'invitation_token', 'user_type', 'survey_status','subscription_active')
        read_only_fields = ('core_user_uuid', 'organization',)

    def get_subscription_active(self, user):
        return user.organization.organization_subscription.filter(
            subscription_end_date__gte=timezone.now().date(),
        ).exists()


class CoreUserWritableSerializer(CoreUserSerializer):
    """
    Override default CoreUser serializer for writable actions (create, update, partial_update)
    """
    password = serializers.CharField(write_only=True)
    organization_name = serializers.CharField(source='organization.name')
    core_groups = serializers.PrimaryKeyRelatedField(many=True, queryset=CoreGroup.objects.all(), required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = CoreUser
        fields = CoreUserSerializer.Meta.fields + ('password', 'organization_name', 'coupon_code')
        read_only_fields = CoreUserSerializer.Meta.read_only_fields

    def create(self, validated_data):
        # validate coupon code or referral code if used
        coupon_code = validated_data.pop('coupon_code', None)
        referral_code = validated_data.pop('referral_code', None)
        if coupon_code or referral_code:
            if not self.is_coupon_valid(coupon_code or referral_code, is_referral=bool(referral_code)):
                raise serializers.ValidationError(
                    'Invalid coupon code or referral code', code='invalid_code'
                )

        # get or create organization
        organization = validated_data.pop('organization')
        org_name = organization['name']
        organization, is_new_org = Organization.objects.get_or_create(name=str(org_name).lower())

        core_groups = validated_data.pop('core_groups', [])
        invitation_token = validated_data.pop('invitation_token', None)
        # create core user
        if settings.AUTO_APPROVE_USER:  # If auto-approval set to true
            validated_data['is_active'] = True
        else:
            validated_data['is_active'] = bool(invitation_token)

        coreuser = CoreUser.objects.create(
            organization=organization,
            **validated_data
        )
        # set user password
        coreuser.set_password(validated_data['password'])
        coreuser.save()

        # check whether org_name is "default"
        if org_name in ['default']:
            default_org_user = (
                CoreGroup.objects
                .filter(organization__name=settings.DEFAULT_ORG, is_org_level=True, permissions=PERMISSIONS_VIEW_ONLY)
                .first()
            )
            coreuser.core_groups.add(default_org_user)

        # check whether an old organization
        if not is_new_org:
            coreuser.is_active = False
            coreuser.save()

            org_user = (
                CoreGroup.objects
                .filter(organization__name=organization, is_org_level=True, permissions=PERMISSIONS_VIEW_ONLY)
                .first()
            )
            coreuser.core_groups.add(org_user)

        # add org admin role to the user if org is new
        if is_new_org:
            organization.unlimited_free_plan = True
            organization.save(update_fields=['unlimited_free_plan'])

            group_org_admin = CoreGroup.objects.get(
                organization=organization, is_org_level=True, permissions=PERMISSIONS_ORG_ADMIN
            )
            coreuser.core_groups.add(group_org_admin)

            if coupon_code or referral_code:
                coupon = self.handle_coupon(coupon_code or referral_code, is_referral=bool(referral_code))
                if coupon:
                    organization.coupon = coupon
                    organization.save(update_fields=['coupon'])

        # add requested groups to the user
        coreuser.core_groups.add(*core_groups)

        # create or update an invitation
        EmailVerificationToken().send_verification_email(self.context['request'], coreuser)
        reg_location = urljoin(settings.FRONTEND_URL, settings.VERIFY_EMAIL_URL_PATH)
        reg_location = reg_location + '{}'
        token = urlsafe_base64_encode(force_bytes(coreuser.core_user_uuid))

        # build the invitation link
        verification_link = self.context['request'].build_absolute_uri(
            reg_location.format(token)
        )

        # create the user context for the E-mail templates
        context = {
            'verification_link': verification_link,
            'user': coreuser,
        }
        subject = 'Account verification required'  # TODO we need to make this dynamic
        template_name = 'email/coreuser/email_verification.txt'
        html_template_name = 'email/coreuser/email_verification.html'
        send_email(coreuser.email, subject, context, template_name, html_template_name)

        return coreuser

    @staticmethod
    def handle_coupon(code, is_referral=False):
        # check if referral link was used
        if is_referral:
            referral: Referral = Referral.objects.filter(code=code).first()
            coupon = referral.coupon
            referral.usage_count += 1
            referral.save(update_fields=['usage_count'])
        # check if coupon code was used
        else:
            coupon = Coupon.objects.filter(code=code).first()

        return coupon

    @staticmethod
    def is_coupon_valid(code, is_referral=False):
        """
        Validate coupon code or referral code
        """
        if is_referral:
            return Referral.objects.filter(code=code, active=True).exists()

        return Coupon.objects.filter(code=code, active=True).exists()


class CoreUserProfileSerializer(serializers.Serializer):
    """ Let's user update his first_name,last_name,title,contact_info,
    password and organization_name """

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    contact_info = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    organization_name = serializers.CharField(required=False)
    user_type = serializers.CharField(required=False)
    survey_status = serializers.BooleanField(required=False)

    class Meta:
        model = CoreUser
        fields = ('first_name', 'last_name', 'password', 'title', 'contact_info', 'organization_name',
                  'user_type', 'survey_status')

    def update(self, instance, validated_data):
        organization_name = validated_data.pop('organization_name', None)

        name = Organization.objects.filter(name=organization_name).first()
        if name is not None:
            instance.organization = name
            instance.organization_name = name

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.title = validated_data.get('title', instance.title)
        instance.contact_info = validated_data.get('contact_info', instance.contact_info)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.survey_status = validated_data.get('survey_status', instance.survey_status)
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        instance.save()

        return instance


class CoreUserInvitationSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(),
                                   min_length=1, max_length=10)


class CoreUserResetPasswordSerializer(serializers.Serializer):
    """Serializer for reset password request data
    """
    email = serializers.EmailField()

    def save(self, **kwargs):
        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)

        email = self.validated_data["email"]

        count = 0
        for user in CoreUser.objects.filter(email=email, is_active=True):
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            context = {
                'password_reset_link': f'{resetpass_url}{uid}/{token}/',
                'user': user,
            }

            # get specific subj and templates for user's organization
            tpl = EmailTemplate.objects.filter(organization=user.organization, type=TEMPLATE_RESET_PASSWORD).first()
            if not tpl:
                tpl = EmailTemplate.objects.filter(organization__name=settings.DEFAULT_ORG,
                                                   type=TEMPLATE_RESET_PASSWORD).first()
            if tpl and tpl.template:
                context = Context(context)
                text_content = Template(tpl.template).render(context)
                html_content = Template(tpl.template_html).render(context) if tpl.template_html else None
                count += send_email_body(email, tpl.subject, text_content, html_content)
                continue

            # default subject and templates
            subject = 'Reset your password'
            template_name = 'email/coreuser/password_reset.txt'
            html_template_name = 'email/coreuser/password_reset.html'
            count += send_email(email, subject, context, template_name, html_template_name)

        return count


class CoreUserResetPasswordCheckSerializer(serializers.Serializer):
    """Serializer for checking token for resetting password
    """
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        # Decode the uidb64 to uid to get User object
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            self.user = CoreUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CoreUser.DoesNotExist):
            raise serializers.ValidationError({'uid': ['Invalid value']})

        # Check the token
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError({'token': ['Invalid value']})

        return attrs


class CoreUserResetPasswordConfirmSerializer(CoreUserResetPasswordCheckSerializer):
    """Serializer for reset password data
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        password1 = attrs.get('new_password1')
        password2 = attrs.get('new_password2')
        if password1 != password2:
            raise serializers.ValidationError("The two password fields didn't match.")
        password_validation.validate_password(password2, self.user)

        return attrs

    def save(self):
        self.user.set_password(self.validated_data["new_password1"])
        self.user.save()
        return self.user


class OrganizationNestedSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='organization_uuid', read_only=True)
    subscription = serializers.SerializerMethodField()
    subscription_active = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = '__all__'

    def get_subscription(self, organization):
        return SubscriptionSerializer(
            organization.organization_subscription.all(),
            many=True
        ).data

    def get_subscription_active(self, organization):
        return organization.organization_subscription.filter(
            subscription_end_date__gte=timezone.now().date()
        ).exists()


class AccessTokenSerializer(serializers.ModelSerializer):
    user = CoreUserSerializer()

    class Meta:
        model = AccessToken
        fields = ('id', 'user', 'token', 'expires')


class RefreshTokenSerializer(serializers.ModelSerializer):
    access_token = AccessTokenSerializer()
    user = CoreUserSerializer()

    class Meta:
        model = RefreshToken
        fields = ('id', 'user', 'token', 'access_token', 'revoked')


class ApplicationSerializer(serializers.ModelSerializer):
    client_id = serializers.CharField(read_only=True, max_length=100)
    client_secret = serializers.CharField(read_only=True, max_length=255)

    class Meta:
        model = Application
        fields = ('id', 'authorization_grant_type', 'client_id', 'client_secret', 'client_type', 'name',
                  'redirect_uris')

    def create(self, validated_data):
        validated_data['client_id'] = secrets.token_urlsafe(75)
        validated_data['client_secret'] = secrets.token_urlsafe(190)
        return super(ApplicationSerializer, self).create(validated_data)


class CoreUserUpdateOrganizationSerializer(serializers.ModelSerializer):
    """
    Lets user update his  organization_name,and email from the one time pop-up screen.
    Also, this assigns permissions to users
    """

    email = serializers.CharField(required=False)
    organization_name = serializers.CharField(required=False)
    core_groups = CoreGroupSerializer(read_only=True, many=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = CoreUser
        fields = (
            'id',
            'core_user_uuid',
            'first_name',
            'last_name',
            'email',
            'username',
            'is_active',
            'title',
            'contact_info',
            'privacy_disclaimer_accepted',
            'organization_name',
            'organization',
            'core_groups',
            'user_type',
            'survey_status'
        )

    def update(self, instance, validated_data):
        organization_name = str(validated_data.pop('organization_name')).lower()
        instance.email = validated_data.get('email', instance.email)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.survey_status = validated_data.get('survey_status', instance.survey_status)

        if instance.email is not None:
            instance.save()

        is_new_org = Organization.objects.filter(name=organization_name)

        # check whether org_name is "default"
        if organization_name == 'default':
            default_org = Organization.objects.filter(name=settings.DEFAULT_ORG).first()
            instance.organization = default_org
            instance.save()
            # now attach the user role as USER to default organization
            default_org_user = (
                CoreGroup
                .objects
                .filter(
                    organization__name=settings.DEFAULT_ORG,
                    is_org_level=True,
                    permissions=PERMISSIONS_VIEW_ONLY
                )
                .first()
            )
            instance.core_groups.add(default_org_user)

            # remove any other group permissions he is not added
            for single_group in instance.core_groups.all():
                default_org_groups = CoreGroup.objects.filter(
                    organization__name=settings.DEFAULT_ORG,
                    is_org_level=True,
                    permissions=PERMISSIONS_VIEW_ONLY
                )
                if single_group not in default_org_groups:
                    instance.core_groups.remove(single_group)

        # check whether an old organization
        elif is_new_org.exists():

            organization = Organization.objects.get(name=organization_name)
            instance.organization = organization
            instance.is_active = False
            instance.save()
            # now attach the user role as USER
            org_user = (
                CoreGroup
                .objects
                .filter(
                    organization__name=organization_name,
                    is_org_level=True,
                    permissions=PERMISSIONS_VIEW_ONLY
                )
                .first()
            )

            instance.core_groups.add(org_user)

            # remove any other group permissions he is not added
            for single_group in instance.core_groups.all():
                org_groups = CoreGroup.objects.filter(organization__name=organization_name,
                                                      is_org_level=True,
                                                      permissions=PERMISSIONS_VIEW_ONLY)
                if single_group not in org_groups:
                    instance.core_groups.remove(single_group)

        # if the current user is the first user
        elif not is_new_org.exists():
            # first update the org name for that user
            organization = Organization.objects.create(name=organization_name)
            instance.organization = organization

            # activate user
            instance.is_active = True

            # save the user
            instance.save()

            # now attach the user role as ADMIN
            org_admin = (
                CoreGroup
                .objects
                .get(
                    organization=organization,
                    is_org_level=True,
                    permissions=PERMISSIONS_ORG_ADMIN
                )
            )
            instance.core_groups.add(org_admin)

        return instance


class CoreUserEmailNotificationSerializer(serializers.Serializer):
    """
    Serializer for email Notification
    """
    organization_uuid = serializers.UUIDField()
    notification_messages = serializers.CharField()


class PartnerSerializer(serializers.ModelSerializer):
    partner_uuid = serializers.ReadOnlyField()

    class Meta:
        model = Partner
        fields = '__all__'


class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = '__all__'


class CoreUserVerifyEmailSerializer(serializers.Serializer):
    """Serializer for checking token for resetting password
    """
    token = serializers.CharField()

    def validate(self, attrs):
        # Decode the uuid64 to uid to get User object
        try:
            uid = force_str(urlsafe_base64_decode(attrs['token']))
            user = CoreUser.objects.filter(core_user_uuid=uid).first()
            if user:
                user.is_active = True
                user.save()

        except (TypeError, ValueError, OverflowError, CoreUser.DoesNotExist):
            raise serializers.ValidationError({'token': ['Invalid value']})

        return attrs


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'


class CouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Coupon
