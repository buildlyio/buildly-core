import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML, Div
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from workflow.models import CoreUser, Organization

from . import DEMO_BRANCH


class NewUserRegistrationForm(UserCreationForm):
    """
    Form for registering a new account.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def clean_email(self):
        """
        Validate the email field. It has to be unique
        """
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(
                username=username).exists():
            raise forms.ValidationError("Email address is already used.")
        return email

    def __init__(self, *args, **kwargs):
        fname = kwargs.pop('first_name', None)
        lname = kwargs.pop('last_name', None)
        email = kwargs.pop('email', None)
        super(NewUserRegistrationForm, self).__init__(*args, **kwargs)

        self.fields['first_name'].initial = fname
        self.fields['last_name'].initial = lname
        self.fields['email'].initial = email
        if email:
            self.fields['email'].widget.attrs['readonly'] = True

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-sm-2'
    helper.field_class = 'col-sm-6'
    helper.form_error_title = 'Form Errors'
    helper.error_text_inline = True
    helper.help_text_inline = True
    helper.html5_required = True
    helper.form_tag = False


class NewTolaUserRegistrationForm(forms.ModelForm):
    """
    Form for registering a new account.
    """
    class Meta:
        model = CoreUser
        fields = ['title', 'privacy_disclaimer_accepted']

    org = forms.CharField()

    def clean_org(self):
        try:
            org = Organization.objects.get(name=self.cleaned_data['org'])
        except Organization.DoesNotExist:
            raise forms.ValidationError("The Organization was not found.")
        else:
            return org

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset('', 'title', 'org',),
            Fieldset('',
                     HTML("""
                        <div id="iframe" class="mt-2">
                            <h6>Notice/Disclaimer:</h6>
                            <div class="privacy-policy">
                                {% if privacy_disclaimer %}
                                    {{ privacy_disclaimer }}
                                {% else %}
                                    {% include "registration/privacy_policy.html" %}
                                {% endif %}
                            </div>
                        </div>
                     """),  # noqa
                     Div('privacy_disclaimer_accepted',
                         css_class="mt-2")),
        )
        organization = kwargs.pop('org', None)
        super(NewTolaUserRegistrationForm, self).__init__(*args, **kwargs)

        # Set default organization for demo environment
        if settings.DEFAULT_ORG and os.getenv('APP_BRANCH') == DEMO_BRANCH:
            self.fields['org'] = forms.CharField(
                initial=settings.DEFAULT_ORG, disabled=True)
        elif organization:
            self.fields['org'] = forms.CharField(
                initial=organization, disabled=True)

        self.fields['privacy_disclaimer_accepted'].required = True
