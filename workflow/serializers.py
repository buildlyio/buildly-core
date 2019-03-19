from urllib.parse import urljoin

import jwt
from django.contrib.auth import password_validation, get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import Template, Context

from rest_framework import serializers
from rest_framework.reverse import reverse
from workflow import models as wfm
from workflow.email_utils import send_email, send_email_body


User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_self')

    def get_self(self, obj):
        request = self.context['request']
        return reverse('group-detail', kwargs={'pk': obj.id}, request=request)

    class Meta:
        model = Group
        fields = '__all__'


class WorkflowLevel1Serializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.WorkflowLevel1
        fields = '__all__'


class WorkflowLevel1PermissionsSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.DictField())
    role_org = serializers.CharField(required=False)

    def validate_role_org(self, value):
        POSSIBLE_ROLES = (
            'Admin',
            wfm.ROLE_ORGANIZATION_ADMIN,
            wfm.ROLE_VIEW_ONLY
        )
        if value not in POSSIBLE_ROLES:
            raise serializers.ValidationError(
                'Invalid "{}" organization role. Possible values: {}'.format(
                    value, POSSIBLE_ROLES))
        return value


class WorkflowLevel2Serializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.WorkflowLevel2
        fields = '__all__'


class CoreGroupSerializer(serializers.ModelSerializer):

    def _get_current_coreuser(self) -> wfm.CoreUser:
        request = self.context.get("request")
        return request.user if request and hasattr(request, "user") else None

    def create(self, validated_data):
        # set organization
        coreuser = self._get_current_coreuser()
        if coreuser and coreuser.organization:
            validated_data['organization'] = coreuser.organization

        # create core group and permissions
        permissions_data = validated_data.pop('permissions', [])
        coregroup = wfm.CoreGroup.objects.create(**validated_data)
        coregroup.permissions.add(*permissions_data)

        return coregroup

    def update(self, instance, validated_data):
        # update permissions
        new_permissions = validated_data.pop('permissions', [])
        instance.permissions.set(new_permissions)

        return super(CoreGroupSerializer, self).update(instance, validated_data)

    class Meta:
        model = wfm.CoreGroup
        read_only_fields = ('core_group_uuid', 'organization')
        exclude = ('create_date', 'edit_date')


class CoreUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    is_active = serializers.BooleanField(required=False)
    organization_name = serializers.CharField(source='organization.name', write_only=True)
    invitation_token = serializers.CharField(required=False)

    def validate_invitation_token(self, value):
        try:
            jwt.decode(value, settings.SECRET_KEY, algorithms='HS256')
        except jwt.DecodeError:
            raise serializers.ValidationError('Token is not valid.')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Token is expired.')
        return value

    def create(self, validated_data):
        # get or create organization
        organization = validated_data.pop('organization')
        try:
            organization = wfm.Organization.objects.get(**organization)
            is_new_org = False
        except wfm.Organization.DoesNotExist:
            organization = wfm.Organization.objects.create(**organization)
            is_new_org = True

        # create user
        invitation_token = validated_data.pop('invitation_token', None)
        validated_data['is_active'] = is_new_org or bool(invitation_token)
        # create core user
        coreuser = wfm.CoreUser.objects.create(
            organization=organization,
            **validated_data
        )
        # set user password
        coreuser.set_password(validated_data['password'])
        coreuser.save()

        # add org admin role to user if org is new
        if is_new_org:
            group_org_admin = Group.objects.get(name=wfm.ROLE_ORGANIZATION_ADMIN)
            coreuser.groups.add(group_org_admin)

        return coreuser

    class Meta:
        model = wfm.CoreUser
        fields = ('core_user_uuid', 'first_name', 'last_name', 'email', 'username', 'password', 'is_active',
                  'title', 'contact_info', 'privacy_disclaimer_accepted', 'organization', 'core_groups',
                  'organization_name', 'invitation_token')
        read_only_fields = ('core_user_uuid', 'organization', 'core_groups',)
        depth = 1


class CoreUserInvitationSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(),
                                   min_length=1, max_length=10)


class CoreUserResetPasswordSerializer(serializers.Serializer):
    """Serializer for reset password request data
    """
    email = serializers.EmailField()

    def save(self, **kwargs):
        resetpass_url = urljoin(settings.FRONTEND_URL, settings.RESETPASS_CONFIRM_URL_PATH)
        resetpass_url = resetpass_url + '{uid}/{token}/'

        email = self.validated_data["email"]

        count = 0
        for user in User.objects.filter(email=email, is_active=True):
            uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
            token = default_token_generator.make_token(user)
            context = {
                'password_reset_link': resetpass_url.format(uid=uid, token=token),
                'user': user,
            }

            # get specific subj and templates for user's organization
            tpl = wfm.EmailTemplate.objects.filter(organization=user.organization,
                                                   type=wfm.TEMPLATE_RESET_PASSWORD).first()
            if not tpl:
                tpl = wfm.EmailTemplate.objects.filter(organization__name=settings.DEFAULT_ORG,
                                                       type=wfm.TEMPLATE_RESET_PASSWORD).first()
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
            uid = force_text(urlsafe_base64_decode(attrs['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
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


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.Organization
        fields = '__all__'


class InternationalizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.Internationalization
        fields = '__all__'


class WorkflowLevel2NameSerializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.WorkflowLevel2
        fields = ('id', 'name')


class WorkflowLevel2SortSerializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.WorkflowLevel2Sort
        fields = '__all__'


class WorkflowTeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'


class WorkflowTeamListFullSerializer(serializers.ModelSerializer):
    workflowlevel1 = WorkflowLevel1Serializer()

    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'
