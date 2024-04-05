from rest_framework.pagination import (
    CursorPagination,
    PageNumberPagination,
    LimitOffsetPagination,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class DefaultCursorPagination(CursorPagination):
    page_size = 30
    max_page_size = 100
    page_size_query_param = 'page_size'


class DefaultLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 500
