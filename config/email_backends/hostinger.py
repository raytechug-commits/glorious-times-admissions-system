import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
class HostingerEmailBackend(SMTPEmailBackend):
    @property
    def ssl_context(self):
        context = ssl.create_default_context()
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
        return context
