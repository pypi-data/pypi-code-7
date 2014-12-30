from django.db import models

# import pytest; pytest.set_trace()

class TestModel(models.Model):
    name = models.CharField(max_length=100)
