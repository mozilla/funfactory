from django.conf import settings
from django.conf.urls.defaults import patterns
from django.template.loader import BaseLoader

import test_utils
from session_csrf import ANON_COOKIE

from funfactory.admin import site


urlpatterns = patterns('',
    (r'^admin/$', site.urls),
)


class FakeLoader(BaseLoader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        return ('', 'FakeLoader')


class SessionCsrfAdminTests(test_utils.TestCase):
    urls = 'tests.test_admin'

    def setUp(self):
        settings.TEMPLATE_LOADERS = ['tests.test_admin.FakeLoader']

    def test_login_has_csrf(self):
        self.client.get('admin/', follow=True)
        assert self.client.cookies.get(ANON_COOKIE) != None, \
               "Anonymous CSRF Cookie not set."
