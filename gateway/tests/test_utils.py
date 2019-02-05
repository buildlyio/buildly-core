"""pytest unit tests, to run:
DJANGO_SETTINGS_MODULE=bifrost-api.settings.production py.test gateway/tests/test_utils.py -v --cov
or: pytest gateway/tests/test_utils.py
"""

import uuid
import datetime
import pytest

from gateway import utils


def test_json_dump():
    obj = {
        "string": "test1234",
        "integer": 123,
        "array": ['1', 2, ],
        "uuid": uuid.UUID('50096bc6-848a-456f-ad36-3ac04607ff67'),
        "datetime": datetime.datetime(2019, 2, 5, 12, 36, 0, 147972)
    }
    response = utils.json_dump(obj)
    expected_response = '{"string": "test1234",' \
                        ' "integer": 123,' \
                        ' "array": ["1", 2],' \
                        ' "uuid": "50096bc6-848a-456f-ad36-3ac04607ff67",' \
                        ' "datetime": "2019-02-05T12:36:00.147972"}'
    assert response == expected_response


def test_json_dump_exception():

    class TestObj(object):
        pass

    test_obj = TestObj()

    with pytest.raises(TypeError) as exc:
        utils.json_dump(test_obj)

    assert 'is not handled' in str(exc.value)
