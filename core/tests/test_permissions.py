from core.permissions import has_permission, merge_permissions


class TestMergePermissions:
    def test_merge_permissions(self):
        """
        Merge no access to view only permission will result in view only
        """
        result = merge_permissions('0000', '0100')
        assert result == '0100'


class TestHasPermission:
    def test_has_permission_success(self):
        result = has_permission('0100', 'GET')
        assert result

        result = has_permission('0100', 'HEAD')
        assert result

    def test_has_permission_fail(self):
        result = has_permission('0100', 'POST')
        assert not result

        result = has_permission('0100', 'PUT')
        assert not result

    def test_has_permission_no_method(self):
        result = has_permission('0100', 'CONNECT')
        assert not result
