from django.contrib.auth.models import Group, User

from rest_framework import serializers
from rest_framework.reverse import reverse
from workflow import models as wfm


class GroupSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField('get_self')

    def get_self(self, obj):
        request = self.context['request']
        return reverse('group-detail', kwargs={'pk': obj.id}, request=request)

    class Meta:
        model = wfm.Group
        fields = '__all__'


class WorkflowLevel1Serializer(serializers.ModelSerializer):
    workflow_key = serializers.UUIDField(read_only=True)
    id = serializers.ReadOnlyField()

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
    agreement_key = serializers.UUIDField(read_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.WorkflowLevel2
        fields = '__all__'


class CoreUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    password = serializers.CharField(source='user.password', write_only=True)
    is_active = serializers.BooleanField(source='user.is_active',
                                         required=False)
    organization_name = serializers.CharField(source='organization.name',
                                              write_only=True, required=False)
    invitation_token = serializers.CharField(required=False)

    def validate(self, data):
        print(data)
        token = data.get('invitation_token', None)
        email = data.get('user', {}).get('email', None)
        org_name = data.get('organization', {}).get('name', None)
        print(token, email, org_name)
        if not token and (not email or not org_name):
            raise serializers.ValidationError('You must provide either email '
                                              'and organization name or '
                                              'invitation token')
        return data

    @staticmethod
    def _validate_and_get_invitation(data):
        token = data.pop('invitation_token', None)
        try:
            # TODO: think about expiration of the token
            return wfm.Invitation.objects.get(token=token) if token else None
        except wfm.Invitation.DoesNotExist:
            raise serializers.ValidationError(detail="The invitation "
                                                     "token is incorrect")

    def create(self, validated_data):
        # check if invitation exits
        invitation = self._validate_and_get_invitation(validated_data)
        user_data = validated_data.pop('user')

        if invitation:
            organization = invitation.organization
            user_data['email'] = invitation.email
            is_new_org = False
        else:
            # get or create organization
            organization = validated_data.pop('organization')
            try:
                organization = wfm.Organization.objects.get(**organization)
                is_new_org = False
            except wfm.Organization.DoesNotExist:
                organization = wfm.Organization.objects.create(**organization)
                is_new_org = True

        # create user
        user_data['is_active'] = is_new_org or bool(invitation)
        user = User.objects.create(**user_data)

        # add org admin role to user if org is new
        if is_new_org:
            group_org_admin = Group.objects.get(
                name=wfm.ROLE_ORGANIZATION_ADMIN)
            user.groups.add(group_org_admin)

        # set user password
        user.set_password(user_data['password'])
        user.save()

        # create core user
        coreuser = wfm.CoreUser.objects.create(
            user=user,
            organization=organization,
            **validated_data
        )

        # remove invitation on successful registration
        if invitation:
            invitation.delete()

        return coreuser

    class Meta:
        model = wfm.CoreUser
        read_only_fields = ('core_user_uuid', 'organization',)
        exclude = ('create_date', 'edit_date', 'user')
        depth = 1


class CoreUserInvitationSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.EmailField(),
                                   min_length=1, max_length=10)


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.Organization
        fields = '__all__'


class InternationalizationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.Internationalization
        fields = '__all__'


class WorkflowLevel2NameSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.WorkflowLevel2
        fields = ('id', 'name')


class WorkflowLevel2SortSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.WorkflowLevel2Sort
        fields = '__all__'


class WorkflowTeamSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'


class WorkflowTeamListFullSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    workflowlevel1 = WorkflowLevel1Serializer()

    class Meta:
        model = wfm.WorkflowTeam
        fields = '__all__'


class MilestoneSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.Milestone
        fields = '__all__'


class PortfolioSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = wfm.Portfolio
        fields = '__all__'

