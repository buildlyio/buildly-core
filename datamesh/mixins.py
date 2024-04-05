class OrganizationQuerySetMixin(object):
    """
    Adds functionality to return a queryset filtered by the organization_uuid in the JWT header.
    If no jwt header is given, an empty queryset will be returned.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        organization_uuid = self.request.session.get('jwt_organization_uuid', None)
        if not organization_uuid:
            return queryset.none()
        return queryset.filter(organization__organization_uuid=organization_uuid)
