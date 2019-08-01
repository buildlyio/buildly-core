from django import forms
import django_filters

from .models import WorkflowLevel2


class DateRangeWidget(django_filters.widgets.SuffixedMultiWidget):

    suffixes = ['gte', 'lte']

    def __init__(self, attrs=None):
        widgets = (forms.TextInput, forms.TextInput)
        super(DateRangeWidget, self).__init__(widgets, attrs)


class WorkflowLevel2Filter(django_filters.FilterSet):

    create_date = django_filters.DateFromToRangeFilter(widget=DateRangeWidget())

    class Meta:
        model = WorkflowLevel2

        fields = [
            'workflowlevel1__name',
            'workflowlevel1__id',
            'create_date',
            'status__short_name',
            'status__uuid',
        ]
