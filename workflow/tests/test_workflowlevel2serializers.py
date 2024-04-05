from django.test import TestCase
from rest_framework.test import APIRequestFactory

import factories
from ..serializers import WorkflowLevel2NameSerializer


class WorkflowLevel2NameSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        wfl2 = factories.WorkflowLevel2()

        serializer = WorkflowLevel2NameSerializer(instance=wfl2)

        data = serializer.data

        keys = ['level2_uuid', 'name']

        self.assertEqual(set(data.keys()), set(keys))
