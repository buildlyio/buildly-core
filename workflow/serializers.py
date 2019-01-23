from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse
from workflow import models as wfm


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    is_superuser = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    groups = serializers.SerializerMethodField()

    def get_groups(self, obj):
        request = self.context['request']
        groups = obj.groups.all()
        urls_groups = []
        for group in groups:
            urls_groups.append(reverse('group-detail', kwargs={'pk': group.id},
                               request=request))
        return urls_groups

    class Meta:
        model = wfm.User
        exclude = ('password', 'last_login', 'date_joined', 'user_permissions')


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
    username = serializers.CharField(source='user.username', write_only=True)
    password = serializers.CharField(source='user.password', write_only=True)

    def validate_organization(self, value):
        if not wfm.Organization.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                'The Organization "{}" does not exist'.format(value))
        return value

    def create(self, validated_data):
        # create user
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        user.set_password(user_data['password'])
        user.save()

        # create core user
        coreuser = wfm.CoreUser(user=user, **validated_data)
        coreuser.save()
        return coreuser

    class Meta:
        model = wfm.CoreUser
        exclude = ('core_user_uuid', 'create_date', 'edit_date', 'user')


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

