from drf_yasg.openapi import Schema, Parameter, IN_QUERY


TOKEN_QUERY_PARAM = Parameter('token', IN_QUERY, type='string', required=True)

DETAIL_RESPONSE = {
    200: Schema(type='object', properties={'detail': Schema(type='string')})
}

SUCCESS_RESPONSE = {
    200: Schema(type='object', properties={'success': Schema(type='boolean')})
}

COREUSER_INVITE_RESPONSE = {
    200: Schema(
        type='object',
        properties={
            'detail': Schema(type='string'),
            'invitations': Schema(type='array', items=Schema(type='string')),
        },
    )
}

COREUSER_INVITE_CHECK_RESPONSE = {
    200: Schema(
        type='object',
        properties={
            'email': Schema(type='string'),
            'organization': Schema(
                type='object',
                properties={
                    'organization_uuid': Schema(type='string'),
                    'name': Schema(type='string'),
                },
            ),
        },
    )
}

COREUSER_RESETPASS_RESPONSE = {
    200: Schema(
        type='object',
        properties={'detail': Schema(type='string'), 'count': Schema(type='number')},
    )
}
