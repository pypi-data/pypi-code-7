# coding: utf-8

from django.db import models


STATUS_GOOD_CODES = (
    ('S001', u'Пакет не был найден по указанному URL'),
    ('S002', u'Пакет загружен на сервер'),
    ('S004', u'Пакет рассылается'),
    ('S005', u'Пакет отправлен, ожидаем удаление информации о '
             u'пакете из системы'),
    ('S006', u'Во время отправки произошли ошибки'),
    ('S007', u'Некорректный формат пакета'),
    ('S008', u'Превышено время ожидания ответа сервера'),
    ('S009', u'Пакет получен'),
    ('S010', u'Пакет проверяется'),
    ('S011', u'Пакет обрабатывается (формируются сообщения)'),
    ('S012', u'Пакет поставлен в очередь на удаление'),
    ('S013', u'Пакет удален. Рассылка сообщений прекращена'),
    ('S015', u'Количество адресатов превышает установленный лимит'),
    ('S018', u'Пакет отправлен. Информация о пакете удалена'),
    ('S019', u'Пакет проверен, будет разослан в указанное время'),
)
STATUS_ERROR_CODES = (
    ('E000', u'Секретный ключ, указанный в параметрах операции, не опознан'),
    ('E001', u'Не передан URL'),
    ('E002', u'Не передан pack_id'),
    ('E003', u'Информация о пакете не найдена'),
    ('E004', u'Недостаточно трафика'),
    ('E005', u'Не оплачен тариф'),
    ('E006', u'Некорректные данные в пакете'),
)
STATUS_CODES = STATUS_GOOD_CODES + STATUS_ERROR_CODES


class Package(models.Model):

    file = models.FileField(u'пакет в xml-формате',
                            upload_to='django_banzai/package')
    status = models.CharField(u'статус', choices=STATUS_CODES,
                              max_length=4, blank=True)
    pack_id = models.CharField(u'ID пакета в системе', max_length=100,
                               blank=True)

    emails_all = models.PositiveIntegerField(u'emailов всего')
    emails_correct = models.PositiveIntegerField(u'emailов корректных',
                                                 default=0)

    created_on = models.DateTimeField(u'пакет создан', auto_now_add=True)
    description = models.CharField(u'описание пакета', max_length=100,
                                   blank=True)

    class Meta:
        verbose_name = u'пакет'
        verbose_name_plural = u'пакеты'

    def __unicode__(self):
        return u'ID: {0}, Статус: "{1}", Описание пакета: "{2}"'.format(
            self.pk,
            self.status,
            self.description
        )


class Report(models.Model):

    package = models.ForeignKey(Package, verbose_name=u'пакет',
                                related_name='reports')
    status = models.CharField(u'статус', choices=STATUS_CODES,
                              max_length=4, blank=True)

    email = models.EmailField(u'email', blank=True)
    reject_code = models.CharField(u'код ошибки', max_length=250,
                                   blank=True)
    reject_message = models.TextField(u'сообщение об ошибке', blank=True)

    class Meta:
        verbose_name = u'отчёт'
        verbose_name_plural = u'отчёты'

    def __unicode__(self):
        return u'Email: {0}, Код ошибки: "{1}"'.format(
            self.email,
            self.reject_code
        )


class ReportFBL(models.Model):

    package = models.ForeignKey(Package, verbose_name=u'пакет',
                                related_name='reports_fbl')
    status = models.CharField(u'статус', choices=STATUS_CODES,
                              max_length=4, blank=True)
    email = models.EmailField(u'email')

    class Meta:
        verbose_name = u'отчёт о FBL'
        verbose_name_plural = u'отчёты о FBL'

    def __unicode__(self):
        return self.email
