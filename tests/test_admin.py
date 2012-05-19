from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib import admin
import django.contrib.admin.sites
from django.template.loader import BaseLoader
from django.test import TestCase

from mock import patch, Mock
from session_csrf import ANON_COOKIE


urlpatterns = None


def setup():
    global urlpatterns
    urlpatterns = patterns('',
        (r'^admin/$', admin.site.urls),
    )


class FakeLoader(BaseLoader):
    """
    Gets around TemplateNotFound errors by always returning an empty string as
    the template.
    """
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        return ('', 'FakeLoader')


@patch.object(settings, 'TEMPLATE_LOADERS', ['tests.test_admin.FakeLoader'])
class SessionCsrfAdminTests(TestCase):
    urls = 'tests.test_admin'

    @patch.object(django.contrib.admin.sites, 'reverse')
    def test_login_has_csrf(self, reverse):
        reverse = Mock()
        self.client.get('admin/', follow=True)
        assert self.client.cookies.get(ANON_COOKIE), (
            "Anonymous CSRF Cookie not set.")
