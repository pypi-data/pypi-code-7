# coding: utf-8

from hashlib import md5
from urllib import urlencode
from django import forms

from robokassa.conf import LOGIN, PASSWORD1, PASSWORD2
from robokassa.conf import STRICT_CHECK, FORM_TARGET, EXTRA_PARAMS
from robokassa.models import SuccessNotification


class BaseRobokassaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.password1 = kwargs.pop('password1', PASSWORD1)
        self.password2 = kwargs.pop('password2', PASSWORD2)
        self.login = kwargs.pop('login', LOGIN)

        super(BaseRobokassaForm, self).__init__(*args, **kwargs)

        # создаем дополнительные поля
        for key in EXTRA_PARAMS:
            self.fields['shp' + key] = forms.CharField(required=False)
            if 'initial' in kwargs:
                self.fields['shp' + key].initial = kwargs['initial'].get(
                    key, 'None')

    @staticmethod
    def _append_extra_part(standard_part, value_func):
        extra_part = ":".join(
            ["%s=%s" % ('shp' + key, value_func('shp' + key))
             for key in EXTRA_PARAMS])
        if extra_part:
            return ':'.join([standard_part, extra_part])
        return standard_part

    def extra_params(self):
        extra = {}
        for param in EXTRA_PARAMS:
            if ('shp' + param) in self.cleaned_data:
                extra[param] = self.cleaned_data['shp' + param]
        return extra

    def _get_signature(self):
        return md5(self._get_signature_string()).hexdigest().upper()

    def _get_signature_string(self):
        raise NotImplementedError


class RobokassaForm(BaseRobokassaForm):
    # login магазина в обменном пункте
    MrchLogin = forms.CharField(max_length=20)

    # требуемая к получению сумма
    OutSum = forms.DecimalField(
        min_value=0, max_digits=20, decimal_places=2, required=False)

    # номер счета в магазине (должен быть уникальным для магазина)
    InvId = forms.IntegerField(min_value=0, required=False)

    # описание покупки
    Desc = forms.CharField(max_length=100, required=False)

    # контрольная сумма MD5
    SignatureValue = forms.CharField(max_length=32)

    # предлагаемая валюта платежа
    IncCurrLabel = forms.CharField(max_length=10, required=False)

    # e-mail пользователя
    Email = forms.CharField(max_length=100, required=False)

    # язык общения с клиентом (en или ru)
    Culture = forms.CharField(max_length=10, required=False)

    # Параметр с URL'ом, на который форма должны быть отправлена.
    # Может пригодиться для использования в шаблоне.
    target = FORM_TARGET

    def __init__(self, *args, **kwargs):
        super(RobokassaForm, self).__init__(*args, **kwargs)

        # скрытый виджет по умолчанию
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

        self.fields['MrchLogin'].initial = self.login
        self.fields['SignatureValue'].initial = self._get_signature()

    def get_redirect_url(self):
        """
        Получить URL с GET-параметрами, соответствующими значениям полей в
        форме. Редирект на адрес, возвращаемый этим методом, эквивалентен
        ручной отправке формы методом GET.
        """

        def _initial(key, fld):
            val = self.initial.get(key, fld.initial)
            if not val:
                return val
            return unicode(val).encode('1251')

        fields = [
            (name, _initial(name, field))
            for name, field in self.fields.items()
            if _initial(name, field)
        ]
        return self.target + '?' + urlencode(fields)

    def _get_signature_string(self):
        def _val(name):
            if name in self.initial:
                value = self.initial[name]
            else:
                value = self.fields[name].initial
            return '' if value is None else unicode(value)

        standard_part = ':'.join(
            [_val('MrchLogin'), _val('OutSum'), _val('InvId'), self.password1])
        return self._append_extra_part(standard_part, _val)


class ResultURLForm(BaseRobokassaForm):
    """
    Форма для приема результатов и проверки контрольной суммы.
    """

    OutSum = forms.CharField(max_length=15)
    InvId = forms.IntegerField(min_value=0)
    SignatureValue = forms.CharField(max_length=32)

    def clean(self):
        try:
            signature = self.cleaned_data['SignatureValue'].upper()
            if signature != self._get_signature():
                raise forms.ValidationError(u'Ошибка в контрольной сумме')
        except KeyError:
            raise forms.ValidationError(u'Пришли не все необходимые параметры')

        return self.cleaned_data

    def _get_signature_string(self):
        _val = lambda name: unicode(self.cleaned_data[name])
        standard_part = ':'.join(
            [_val('OutSum'), _val('InvId'), self.password2])
        return self._append_extra_part(standard_part, _val)


class _RedirectPageForm(ResultURLForm):
    """
    Форма для проверки контрольной суммы на странице Success.
    """

    Culture = forms.CharField(max_length=10)

    def _get_signature_string(self):
        _val = lambda name: unicode(self.cleaned_data[name])
        standard_part = ':'.join(
            [_val('OutSum'), _val('InvId'), self.password1])
        return self._append_extra_part(standard_part, _val)


class SuccessRedirectForm(_RedirectPageForm):
    """
    Форма для обработки страницы Success с дополнительной защитой. Она
    проверяет, что ROBOKASSA предварительно уведомила систему о платеже,
    отправив запрос на ResultURL.
    """

    def clean(self):
        data = super(SuccessRedirectForm, self).clean()
        if STRICT_CHECK:
            if not SuccessNotification.objects.filter(InvId=data['InvId']):
                raise forms.ValidationError(
                    u'От ROBOKASSA не было предварительного уведомления'
                )
        return data


class FailRedirectForm(BaseRobokassaForm):
    """
    Форма приема результатов для перенаправления на страницу Fail.
    """

    OutSum = forms.CharField(max_length=15)
    InvId = forms.IntegerField(min_value=0)
    Culture = forms.CharField(max_length=10)
