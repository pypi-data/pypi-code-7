import requests
from lxml import etree

from django.contrib.sites.models import Site

from banzai.models import Report, ReportFBL
from banzai.settings import (BANZAI_API_DOMAIN, BANZAI_API_VERSION,
                             BANZAI_API_KEY)


class BanzaiAPI(object):

    def __init__(self, package_obj):
        self._package = package_obj
        self._package_url = None

        self._api_key = BANZAI_API_KEY
        self._base_api_url = 'http://{0}/api/{1}/'.format(BANZAI_API_DOMAIN,
                                                          BANZAI_API_VERSION)

    @property
    def package_url(self):
        if self._package_url is None:
            current_site = Site.objects.get_current()
            url = 'http://{0}{1}'.format(
                current_site.domain,
                self._package.file.url
            )
            self._package_url = url
        return self._package_url

    def _api_url(self, method):
        return '{0}{1}'.format(self._base_api_url, method)

    def _parse_xml(self, data):
        parser = etree.XMLParser()
        parser.feed(data)
        return parser.close()

    def add(self):
        get_params = {'key': self._api_key, 'url': self.package_url}
        req = requests.get(self._api_url('add_package'), params=get_params)

        elem = self._parse_xml(req.content)

        pack_id = elem.find('pack_id')
        if pack_id is not None:
            self._package.pack_id = pack_id.text

        status = elem.find('status')
        if status is not None:
            self._package.status = status.text

        self._package.save()
        return self._package

    def fast_add(self):
        get_params = {'key': self._api_key}
        post_data = {
            'package': self._package.file.read(),
            'description': self._package.description
        }
        req = requests.post(self._api_url('fast_add_package'),
                            params=get_params, data=post_data)

        elem = self._parse_xml(req.content)

        pack_id = elem.find('pack_id')
        if pack_id is not None:
            self._package.pack_id = pack_id.text

        status = elem.find('status')
        if status is not None:
            self._package.status = status.text

        user_count = elem.find('user_count')
        if user_count is not None:
            self._package.emails_correct = user_count.text

        self._package.save()
        return self._package

    def check(self):
        get_params = {'key': self._api_key}
        post_data = {
            'package': self._package.file.read(),
        }
        req = requests.post(self._api_url('check_package'),
                            params=get_params, data=post_data)

        elem = self._parse_xml(req.content)

        status = elem.find('status')
        if status is not None:
            self._package.status = status.text

        user_count = elem.find('user_count')
        if user_count is not None:
            self._package.emails_correct = user_count.text

        self._package.save()
        return {
            'status': self._package.status,
            'emails_correct': self._package.emails_correct
        }

    def status(self):
        get_params = {'key': self._api_key, 'pack_id': self._package.pack_id}
        req = requests.get(self._api_url('package_status'), params=get_params)

        elem = self._parse_xml(req.content)

        status = elem.find('status')
        if status is not None:
            self._package.status = status.text

        self._package.save()
        return self._package.status

    def report(self):
        get_params = {'key': self._api_key, 'pack_id': self._package.pack_id}
        req = requests.get(self._api_url('package_report'), params=get_params)

        elem = self._parse_xml(req.content)

        items = elem.findall('item')
        for item in items:
            email = ''
            reject_code = ''
            reject_message = ''

            email_elem = item.find('email')
            if email_elem is not None:
                email = email_elem.text

            code_elem = item.find('code')
            if code_elem is not None:
                reject_code = code_elem.text

            message_elem = item.find('message')
            if message_elem is not None:
                reject_message = message_elem.text

            report_obj, _ = Report.objects.get_or_create(
                package=self._package,
                email=email,
                reject_code=reject_code,
                reject_message=reject_message,
            )
        else:
            status = elem.find('status')
            if status is not None:
                report_obj, _ = Report.objects.get_or_create(
                    package=self._package,
                    status=status.text
                )
        return self._package.reports.all()

    def report_fbl(self):
        get_params = {'key': self._api_key, 'pack_id': self._package.pack_id}
        req = requests.get(self._api_url('package_report_fbl'),
                           params=get_params)

        elem = self._parse_xml(req.content)

        items = elem.findall('item')
        for item in items:
            email = ''

            email_elem = item.find('email')
            if email_elem is not None:
                email = email_elem.text

            report_obj, _ = ReportFBL.objects.get_or_create(
                package=self._package,
                email=email,
            )
        else:
            status = elem.find('status')
            if status is not None:
                report_obj, _ = ReportFBL.objects.get_or_create(
                    package=self._package,
                    status=status.text
                )
        return self._package.reports_fbl.all()

    def stop(self):
        pass
