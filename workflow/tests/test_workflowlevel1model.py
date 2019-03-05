import pytest

import workflow.models as wfm
from .fixtures import org


@pytest.mark.django_db()
class TestWorkflowLevel1Model:

    def test_create(self, org):
        wfl1 = wfm.WorkflowLevel1.objects.create(name='New program', organization=org)
        core_groups = wfl1.core_groups.all()
        assert len(core_groups) == 2
        groups = [f'{wfm.ROLE_PROGRAM_ADMIN} ({wfl1.organization}, {wfl1.pk})',
                  f'{wfm.ROLE_PROGRAM_TEAM} ({wfl1.organization}, {wfl1.pk})']
        for item in core_groups:
            assert item.group.name in groups

    def test_update(self, org):
        wfl1 = wfm.WorkflowLevel1.objects.create(name='New program', organization=org)
        wfl1.name = 'Fixed name'
        wfl1.save()
        assert len(wfl1.core_groups.all()) == 2
