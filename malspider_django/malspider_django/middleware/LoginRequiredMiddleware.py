from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware:
    def process_request(self, request):
        if hasattr(settings, 'AUTHENTICATION_BACKENDS') and len(settings.AUTHENTICATION_BACKENDS) > 0:
            if not request.user.is_authenticated():
                path = request.path_info.lstrip('/')
                if not any(m.match(path) for m in EXEMPT_URLS):
                    return HttpResponseRedirect(settings.LOGIN_URL)
