import traceback
import logging
import os

logger = logging.getLogger('exception_logger')

class ExceptionLoggingMiddleware:
    """Middleware that logs full tracebacks of unhandled exceptions to server-exceptions.log
    to aid debugging on development machines where stdout may be redirected.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as exc:
            tb = traceback.format_exc()
            try:
                with open('server-exceptions.log', 'a', encoding='utf-8') as f:
                    f.write('\n' + ('='*80) + '\n')
                    f.write(tb)
            except Exception:
                logger.exception('Failed to write server-exceptions.log')
            # re-raise so normal Django error handling continues
            raise

class SecurityHeadersMiddleware:
    """Add additional security headers (CSP, Referrer-Policy, Permissions-Policy).
    CSP value can be overridden with the CSP_HEADER env var.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.csp = os.getenv('CSP_HEADER', "default-src 'self'; img-src 'self' data:; media-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault('Content-Security-Policy', self.csp)
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        return response
