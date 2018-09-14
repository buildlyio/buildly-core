# -*- coding: utf-8 -*-
from django.test import TestCase
from rest_framework.test import APIRequestFactory

import factories
from ..serializers import WorkflowLevel2NameSerializer


class WorkflowLevel2NameSerializerTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_contains_expected_fields(self):
        appointment = factories.WorkflowLevel2()

        serializer = WorkflowLevel2NameSerializer(instance=appointment)

        data = serializer.data

        keys = [
            'id',
            'name'
        ]

        self.assertEqual(set(data.keys()), set(keys))
