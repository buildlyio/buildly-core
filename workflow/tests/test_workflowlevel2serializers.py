# -*- coding: utf-8 -*-
from django.test import TestCase
from rest_framework.test import APIRequestFactory

import factories
from ..serializers import WorkflowLevel2NameSerializer, WorkflowLevel2Serializer


class Workflowlevel2SerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        wfl2 = factories.WorkflowLevel2()

        serializer = WorkflowLevel2Serializer(instance=wfl2)

        data = serializer.data

        keys = [
            'name',
            'level2_uuid',
            'workflowlevel1',
            'short_name',
            'description',
            'type',
            'notes',
            'parent_workflowlevel2',
            'start_date',
            'end_date',
            'core_groups',
            'edit_date',
            'create_date',
            'created_by',
        ]

        self.assertEqual(set(data.keys()), set(keys))


class WorkflowLevel2NameSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        wfl2 = factories.WorkflowLevel2()

        serializer = WorkflowLevel2NameSerializer(instance=wfl2)

        data = serializer.data

        keys = [
            'level2_uuid',
            'name'
        ]

        self.assertEqual(set(data.keys()), set(keys))
