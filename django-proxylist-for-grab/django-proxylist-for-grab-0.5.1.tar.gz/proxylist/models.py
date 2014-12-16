# -*- coding: utf-8 -*-

import socket
import random
import json
import os

from datetime import timedelta
from random import randint
from pygeoip import GeoIP
from grab import Grab

from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.db import models
from django import VERSION

try:
    from django_countries import CountryField
except ImportError:
    from django_countries.fields import CountryField

from proxylist import now, parse
from proxylist import defaults


ANONYMITY_NONE = 0
ANONYMITY_LOW = 1
ANONYMITY_MEDIUM = 2
ANONYMITY_HIGH = 3

PROXY_TYPE_CHOICES = (
    ('http', 'HTTP'),
    ('https', 'HTTPS'),
    ('socks4', 'SOCKS4'),
    ('socks5', 'SOCKS5'),
)


class ProxyCheckResult(models.Model):
    """The result of a proxy check"""

    mirror = models.ForeignKey('Mirror', verbose_name=_('Mirror'))

    proxy = models.ForeignKey('Proxy', verbose_name=_('Proxy'))

    #: Our real outbound IP Address (from worker)
    real_ip_address = models.IPAddressField(
        _('Real IP address'), blank=True, null=True)

    #: Proxy outbound IP Address (received from mirror)
    hostname = models.CharField(
        _('Hostname'), max_length=25, blank=True, null=True)

    #: True if we found proxy related http headers
    forwarded = models.BooleanField(_('Forwarded'), default=True)

    #: True if `real_ip_address` was found at any field
    ip_reveal = models.BooleanField(_('IP reveal'), default=True)

    #: Check starts
    check_start = models.DateTimeField(_('Check start'))

    #: Request was received at mirror server
    response_start = models.DateTimeField(_('Response start'))

    #: Request was send back from the mirror
    response_end = models.DateTimeField(_('Response end'))

    #: Check ends
    check_end = models.DateTimeField(_('Check end'))

    raw_response = models.TextField(_('Raw response'), null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(ProxyCheckResult, self).__init__(*args, **kwargs)
        if self.real_ip_address is None:
            self.real_ip_address = self._get_real_ip()

    class Meta:
        verbose_name = _('Proxy check results')
        verbose_name_plural = _('Proxy check results')

    def __unicode__(self):
        return str(self.check_start)

    @staticmethod
    def _get_real_ip():
        ip_key = '%s.%s.ip' % (socket.gethostname(), os.getpid())
        ip = cache.get(ip_key)
        if ip:
            return ip

        g = Grab(
            hammer_mode=True,
            hammer_timeouts=defaults.GRABBER_HAMMER_TIMEOUTS,
            connect_timeout=15,
            timeout=30
        )
        g.go("http://ifconfig.me/ip")
        ip = g.response.body.strip()

        cache.set(ip_key, ip, defaults.PROXY_LIST_OUTIP_INTERVAL)
        return ip

    def anonymity(self):
        if self.forwarded and self.ip_reveal:
            return ANONYMITY_NONE
        elif not self.forwarded and self.ip_reveal:
            return ANONYMITY_LOW
        elif self.forwarded and not self.ip_reveal:
            return ANONYMITY_MEDIUM
        else:
            return ANONYMITY_HIGH


class Mirror(models.Model):
    """
    A proxy checker site like.
    Ex: http://ifconfig.me/all.json
    """
    url = models.URLField(
        _('URL'), help_text=_('For example: http://local.com/mirror'))

    output_type = models.CharField(
        _('Output type'), max_length=10, default='plm_v1', choices=(
            ('plm_v1', _('ProxyList Mirror v1.0')),
        )
    )

    class Meta:
        verbose_name = _('Mirror')
        verbose_name_plural = _('Mirrors')

    def __unicode__(self):
        return self.url

    def _make_request(self, proxy):
        """
        Make request to the mirror proxy
        """
        auth = None
        if proxy.user and proxy.password:
            auth = '%s:%s' % (proxy.user, proxy.password)

        g = Grab()
        g.setup(
            connect_timeout=defaults.PROXY_LIST_CONNECTION_TIMEOUT,
            timeout=defaults.PROXY_LIST_CONNECTION_TIMEOUT,
            proxy='%s:%d' % (proxy.hostname, proxy.port),
            proxy_type=proxy.proxy_type,
            proxy_userpwd=auth,
            user_agent=defaults.PROXY_LIST_USER_AGENT,
            hammer_mode=False,
        )
        g.go(str(self.url))
        return g.response

    @staticmethod
    def _parse_plm_v1(res, raw_data):
        """
        Parse data from a ProxyList Mirror v1.0 output and fill a
        ProxyCheckResult object
        """

        forward_headers = {
            'FORWARDED',
            'X_FORWARDED_FOR',
            'X_FORWARDED_BY',
            'X_FORWARDED_HOST',
            'X_FORWARDED_PROTO',
            'VIA',
            'CUDA_CLIIP',
        }

        data = json.loads(raw_data)

        res.response_start = parse(data['response_start'])
        res.response_end = parse(data['response_end'])

        res.hostname = data.get('REMOTE_ADDR', None)

        # True if we found proxy related http headers
        headers_keys = data['http_headers'].keys()
        res.forwarded = bool(forward_headers.intersection(headers_keys))

        headers_values = data['http_headers'].values()

        #: True if `real_ip_address` was found at any field
        res.ip_reveal = any(
            [x.find(res.real_ip_address) != -1 for x in headers_values])

    @staticmethod
    def is_checking(proxy):
        return bool(cache.get("proxy.%s.check" % proxy.pk))

    def _get_elapsed_time(self, proxy):
        time = []
        req_range = defaults.CALCULATE_ELAPSED_TIME_REQUESTS_RANGE
        for i in range(random.choice(req_range)):
            try:
                time.append(self._make_request(proxy).total_time)
            except Exception, msg:
                print msg.__str__()
        return sum(time) / float(len(time))

    def _check_proxy(self, proxy):
        """Do a proxy check"""

        check_key = "proxy.%s.check" % proxy.pk

        try:
            res = ProxyCheckResult()
            res.proxy = proxy
            res.mirror = self
            res.check_start = now()
            response = self._make_request(proxy)
            raw_data = response.body
            try:
                elapsed_time = '%1.2f' % self._get_elapsed_time(proxy)
            except:
                elapsed_time = response.total_time
            res.check_end = now()
            res.raw_response = raw_data

            if self.output_type == 'plm_v1':
                self._parse_plm_v1(res, raw_data)
            else:
                raise Exception('Output type not found!')

            proxy.update_from_check(res, elapsed_time)

            res.save()

            return res
        except:
            proxy.update_from_error()
            raise
        finally:
            # Task unlock
            cache.delete(check_key)

    def check_proxy(self, proxy, async=True):
        if defaults.PROXY_LIST_USE_CELERY and async:
            from proxylist.tasks import async_check

            check_key = "proxy.%s.check" % proxy.pk

            if self.is_checking(proxy):
                return None
            else:
                # Task lock
                cache.add(check_key, "true", defaults.PROXY_LIST_CACHE_TIMEOUT)

            return async_check.apply_async((proxy.pk, self.pk))
        return self._check_proxy(proxy)


class Proxy(models.Model):
    """A proxy server"""

    _geoip = GeoIP(defaults.PROXY_LIST_GEOIP_PATH)

    anonymity_level_choices = (
        # Anonymity can't be determined
        (None, _('Unknown')),

        # No anonymity; remote host knows your IP and knows you are using
        # proxy.
        (ANONYMITY_NONE, _('None')),

        # Low anonymity; proxy sent our IP to remote host, but it was sent in
        # non standard way (unknown header).
        (ANONYMITY_LOW, _('Low')),

        # Medium anonymity; remote host knows you are using proxy, but it does
        # not know your IP
        (ANONYMITY_MEDIUM, _('Medium')),

        # High anonymity; remote host does not know your IP and has no direct
        # proof of proxy usage (proxy-connection family header strings).
        (ANONYMITY_HIGH, _('High')),
    )

    hostname = models.CharField(_('Hostname'), max_length=75)
    port = models.PositiveIntegerField(_('Port'))
    user = models.CharField(_('User'), blank=True, null=True, max_length=50)
    password = models.CharField(
        _('Password'), blank=True, null=True, max_length=50)

    country = CountryField(
        _('Country'), null=True, blank=True, editable=False)

    proxy_type = models.CharField(
        _('Proxy type'), default='http',
        max_length=10, choices=PROXY_TYPE_CHOICES)

    anonymity_level = models.PositiveIntegerField(
        _('Anonymity level'), null=True, default=ANONYMITY_NONE,
        choices=anonymity_level_choices, editable=False)

    last_check = models.DateTimeField(
        _('Last check'), null=True, blank=True, editable=False)

    next_check = models.DateTimeField(
        _('Next check'), null=True, blank=True)

    created = models.DateTimeField(
        _('Created'), auto_now=False, auto_now_add=True,
        db_index=True, editable=False)

    errors = models.PositiveIntegerField(
        _('Errors'), default=0, editable=False)

    elapsed_time = models.FloatField(
        _('Elapsed time'), blank=True, null=True, editable=False)

    def _update_next_check(self):
        """ Calculate and set next check time """

        delay = randint(defaults.PROXY_LIST_MIN_CHECK_INTERVAL,
                        defaults.PROXY_LIST_MAX_CHECK_INTERVAL)

        delay += defaults.PROXY_LIST_ERROR_DELAY * self.errors

        if self.last_check:
            self.next_check = self.last_check + timedelta(seconds=delay)
        else:
            self.next_check = now() + timedelta(seconds=delay)

    def update_from_check(self, check, elapsed_time):
        """ Update data from a ProxyCheckResult """

        if check.check_start:
            self.last_check = check.check_start
        else:
            self.last_check = now()
        self.errors = 0
        self.anonymity_level = check.anonymity()
        self._update_next_check()
        self.elapsed_time = elapsed_time
        self.save()

    def update_from_error(self):
        """ Last check was an error """

        self.last_check = now()
        self.errors += 1
        self._update_next_check()
        self.save()

    def save(self, *args, **kwargs):
        if not self.country:
            if self.hostname.count('.') == 3:
                self.country = self._geoip.country_code_by_addr(str(
                    self.hostname
                ))
            else:
                self.country = self._geoip.country_code_by_name(str(
                    self.hostname
                ))

        if not self.next_check:
            self.next_check = (now() - timedelta(
                seconds=defaults.PROXY_LIST_MAX_CHECK_INTERVAL))

        super(Proxy, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Proxy')
        verbose_name_plural = _('Proxies')
        ordering = ('-last_check',)
        unique_together = (('hostname', 'port'),)
        if VERSION >= (1, 5):
            index_together = (
                ('errors', 'last_check', 'anonymity_level'),
                ('errors', 'last_check'),
            )

    def __unicode__(self):
        return "%s://%s:%s" % (self.proxy_type, self.hostname, self.port)


class Upload(models.Model):
    file_name = models.FileField(
        _('File'), upload_to='proxies',
        help_text=_('File format: proxy:port@user:password'))
    created = models.DateTimeField(
        _('Created'), auto_now=False, auto_now_add=True, editable=False)
    proxy_type = models.CharField(
        _('Proxy type'), default='http',
        max_length=10, choices=PROXY_TYPE_CHOICES)

    def __unicode__(self):
        return unicode(self.file_name)

    class Meta:
        verbose_name = _('Upload')
        verbose_name_plural = _('Uploads')


class ProxyList(models.Model):
    url = models.URLField(_('URL'), unique=True)
    update_period = models.IntegerField(_('Update period'), default=300)
    next_check = models.DateTimeField(
        _('Next check'), null=True, blank=True,
        editable=False, auto_now_add=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    def __unicode__(self):
        return unicode(self.url)

    class Meta:
        verbose_name = _('Proxylist urls')
        verbose_name_plural = _('Proxylist urls')
