import logging
import urllib.parse

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.conf import settings

from social_core.pipeline.partial import partial

from workflow.models import CoreSites, Organization

logger = logging.getLogger(__name__)


def redirect_after_login(strategy, *args, **kwargs):
    redirect = strategy.session_get('redirect_after_login')
    strategy.session_set('next', redirect)


@partial
def check_user(strategy, details, backend, user=None, *args, **kwargs):
    """
    Redirect the user to the registration page, if we haven't found
    a user account yet.
    """
    if user:
        return {'is_new': False}
    try:
        user = User.objects.get(first_name=details['first_name'],
                                last_name=details['last_name'],
                                email=details['email'])
        return {
            'is_new': True,
            'user': user
        }
    except User.DoesNotExist:
        current_partial = kwargs.get('current_partial')
        query_params = {
            'cus_fname': details['first_name'].encode('utf8'),
            'cus_lname': details['last_name'].encode('utf8'),
            'cus_email': details['email'].encode('utf8'),
            'organization_uuid': details['organization_uuid'],
            'partial_token': current_partial.token
        }
        qp = urllib.parse.urlencode(query_params)
        redirect_url = u'/accounts/register/?{}'.format(qp)
        return HttpResponseRedirect(redirect_url)


def auth_allowed(backend, details, response, *args, **kwargs):
    """
    Verifies that the current auth process is valid. Emails,
    domains whitelists and organization domains are applied (if defined).
    """
    allowed = False
    static_url = settings.STATIC_URL

    # Get whitelisted domains and emails defined in the settings
    whitelisted_emails = backend.setting('WHITELISTED_EMAILS', [])
    whitelisted_domains = backend.setting('WHITELISTED_DOMAINS', [])

    # Get the whitelisted domains defined in the CoreSites
    site = get_current_site(None)

    core_site = CoreSites.objects.filter(site=site).first()
    if core_site and core_site.whitelisted_domains:
        core_domains = ','.join(core_site.whitelisted_domains.split())
        core_domains = core_domains.split(',')
        whitelisted_domains += core_domains

    try:
        email = details['email']
    except KeyError:
        logger.warning('No email was passed in the details.')
        allowed = False
    else:
        domain = email.split('@', 1)[1]
        if whitelisted_emails or whitelisted_domains:
            allowed = (email in whitelisted_emails or domain in
                       whitelisted_domains)

        # Check if the user email domain matches with one of the org oauth
        # domains and add the organization uuid in the details
        if allowed:
            org_uuid = Organization.objects.values_list(
                'organization_uuid', flat=True).get(name=settings.DEFAULT_ORG)
            details.update({'organization_uuid': org_uuid})
        else:
            try:
                org_uuid = Organization.objects.values_list(
                    'organization_uuid', flat=True).get(
                    oauth_domains__contains=[domain])
                details.update({'organization_uuid': org_uuid})
                allowed = True
            except Organization.DoesNotExist:
                pass
            except Organization.MultipleObjectsReturned as e:
                logger.warning('There is more than one Organization with '
                               'the domain {}.\n{}'.format(domain, e))

    if not allowed:
        return render_to_response('unauthorized.html',
                                  context={'STATIC_URL': static_url})
