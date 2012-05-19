import jingo
import jinja2
from nose.tools import eq_
from django.test import TestCase, RequestFactory

from mock import patch

import funfactory.context_processors


class TestContext(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def render(self, content, request=None):
        if not request:
            request = self.factory.get('/')
        tpl = jinja2.Template(content)
        return jingo.render_to_string(request, tpl)

    def test_request(self):
        eq_(self.render('{{ request.path }}'), '/')

    def test_settings(self):
        eq_(self.render('{{ settings.SITE_ID }}'), '1')

    def test_languages(self):
        eq_(self.render("{{ LANGUAGES['en-us'] }}"), 'English (US)')

    @patch.object(funfactory.context_processors, 'translation')
    def test_languages(self, translation):
        translation.get_language.return_value = 'en-US'
        eq_(self.render("{{ LANG }}"), 'en-US')

    def test_lang_dir(self):
        eq_(self.render("{{ DIR }}"), 'ltr')
