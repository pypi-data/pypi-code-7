from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from dynamicForms.models import Form, Version


modified_logic = Signal(providing_args=["sent_data"])
