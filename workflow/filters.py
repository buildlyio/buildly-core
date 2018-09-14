import django_filters
from workflow.models import Dashboard


class DashboardFilter(django_filters.FilterSet):
    public = django_filters.CharFilter(
        method="public_filter",
        help_text='Can either be all, org or url')

    class Meta:
        model = Dashboard
        fields = ['user', 'share']

    def public_filter(self, queryset, name, value):
        if value == 'all':
            return queryset.filter(public__all=True)
        elif value == 'org':
            return queryset.filter(public__org=True)
        elif value == 'url':
            return queryset.filter(public__url=True)
