from django.contrib.admin.sites import AdminSite

from session_csrf import anonymous_csrf


class SessionCsrfAdminSite(AdminSite):
    """Custom admin site that handles login with session_csrf."""

    def login(self, request, extra_context=None):
        @anonymous_csrf
        def call_parent_login(request, extra_context):
            return super(SessionCsrfAdminSite, self).login(request,
                                                           extra_context)

        return call_parent_login(request, extra_context)

site = SessionCsrfAdminSite()
