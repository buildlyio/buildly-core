from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class DefaultCursorPagination(CursorPagination):
    """
    TODO move this to settings to provide better standardization
    See http://www.django-rest-framework.org/api-guide/pagination/
    """
    page_size = 30
    max_page_size = 100
    page_size_query_param = 'page_size'
