import pytest

import workflow.models as wfm


@pytest.mark.django_db()
class TestOrganizationModel:

    def test_create(self):
        org = wfm.Organization.objects.create(name='New organization')
        core_groups = org.core_groups.all()
        assert len(core_groups) == 2
        groups = [f'{wfm.ROLE_ORGANIZATION_ADMIN} ({org.name})', f'{wfm.ROLE_VIEW_ONLY} ({org.name})']
        for item in core_groups:
            assert item.group.name in groups

    def test_update(self):
        org = wfm.Organization.objects.create(name='New organization')
        org.name = 'Fixed name'
        org.save()
        assert len(org.core_groups.all()) == 2
