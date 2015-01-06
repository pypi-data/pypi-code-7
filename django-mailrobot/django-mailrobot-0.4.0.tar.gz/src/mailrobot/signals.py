import django.dispatch

__all__ = ['mail_sent']

mail_sent = django.dispatch.Signal(providing_args=["mail", "context"])
