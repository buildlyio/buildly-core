import pytest

from unittest.mock import Mock

from gateway import utils
from gateway.tests.fixtures import aggregator, logic_module


@pytest.mark.django_db()
class TestSwaggerAggregator:
    def test_get_aggregate_swagger_without_api_specification(
        self, aggregator, logic_module, monkeypatch
    ):
        test_swagger = {'name': 'test'}
        mocked_swagger = Mock()
        mocked_swagger.return_value.json.return_value = test_swagger
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        result = aggregator.get_aggregate_swagger()
        for api_name, api_url in aggregator.configuration['apis'].items():
            assert api_name in result
            assert result[api_name]['url'] == api_url
            assert result[api_name]['spec'] == test_swagger

        mocked_swagger.assert_called_once()

    def test_get_aggregate_swagger_with_api_specification(
        self, aggregator, logic_module, monkeypatch
    ):
        test_swagger = {'name': 'test'}
        logic_module.api_specification = test_swagger
        logic_module.save()

        mocked_swagger = Mock()
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        result = aggregator.get_aggregate_swagger()
        for api_name, api_url in aggregator.configuration['apis'].items():
            assert api_name in result
            assert result[api_name]['url'] == api_url
            assert result[api_name]['spec'] == test_swagger

        mocked_swagger.assert_not_called()

    def test_get_aggregate_swagger_connection_error(
        self, aggregator, logic_module, monkeypatch
    ):
        mocked_swagger = Mock(side_effect=ConnectionError)
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        result = aggregator.get_aggregate_swagger()
        assert result == {}
        mocked_swagger.assert_called_once()

    def test_get_aggregate_swagger_timeout_error(
        self, aggregator, logic_module, monkeypatch
    ):
        mocked_swagger = Mock(side_effect=TimeoutError)
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        result = aggregator.get_aggregate_swagger()
        assert result == {}
        mocked_swagger.assert_called_once()

    def test_get_aggregate_swagger_value_error(
        self, aggregator, logic_module, monkeypatch
    ):
        mocked_swagger = Mock(side_effect=ValueError)
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        result = aggregator.get_aggregate_swagger()
        assert result == {}
        mocked_swagger.assert_called_once()
