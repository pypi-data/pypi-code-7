# coding: utf-8
from __future__ import unicode_literals

from django.dispatch import Signal

bounce_received = Signal(providing_args=["mail_obj", "bounce_obj", "raw_message"])

complaint_received = Signal(providing_args=["mail_obj", "complaint_obj", "raw_message"])
