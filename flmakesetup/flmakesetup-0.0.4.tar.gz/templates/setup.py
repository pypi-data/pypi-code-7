from setuptools import setup

setup(
    name="{{name}}",
    version="{{version}}",
    auther="{{auther}}",
    auther_email="{{auther_email}}",
    {% if description %}
    description="{{description}}",
    {% endif %}
    {% if url %}
    url="{{url}}",
    {% endif %}
    {% if test_suite %}
    test_suite="{{test_suite}}",
    {% endif %}
    {% if license %}
    license="{{license}}",
    {% endif %}
)
