# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.cache import cache
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.utils._os import safe_join

from cmstemplates.models import TemplateZone, TemplateFile


class Loader(BaseLoader):
    """
    Загружает шаблоны для зоны с диска, базы данных, кеша в зависимости
    от настроек шаблона и наличия его в кеше.
    """

    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        if template_name.endswith('.html'):
            raise TemplateDoesNotExist('zone name can not end with ".html"')
        # имя зоны в template_name
        source = []
        dirs = []

        zone_templates_dir = getattr(settings, 'ZONE_TEMPLATES_DIR', 'zone_templates')

        cache_key = 'cmstemplates:%s' % template_name
        cached = cache.get(cache_key)
        if cached is not None:
            return cached['source'], cached['dirs']
        else:
            # все активные шаблоны для зоны
            files = TemplateFile.objects.filter(
                zone__name=template_name,
                is_active=True
            ).order_by('weight')

            if not files:
                # если нет файлов и нет зоны - вызвать исключение
                if not TemplateZone.objects.filter(name=template_name).count():
                    error_msg = "No files for zone %s" % template_name
                    # raise TemplateDoesNotExist(error_msg)
                    TemplateZone.objects.create(
                        name=template_name,
                        description=u'Создана автоматически',
                    )
                # если зона есть, но нет файлов - она пустая, игнорировать
                # и занести в кеш, который инвалидируется при добавлении шаблона
                else:
                    cache.set(cache_key, {'source': '', 'dirs': ''})
            # открыть все файлы и склеить их содержимое в один шаблон для всей зоны
            for f in files:
                if f.only_for_superuser:
                    only_for_superuser_text_pre = u'{% if request.user.is_superuser %}'
                    only_for_superuser_text_post = u'{% endif %}'
                else:
                    only_for_superuser_text_pre = u''
                    only_for_superuser_text_post = u''
                if f.use_content:
                    content = u'{} {} {}'.format(
                        only_for_superuser_text_pre,
                        f.template_content,
                        only_for_superuser_text_post
                    )
                    source.append(content)
                    dirs.append('template %s content' % f.id)
                else:
                    try:
                        # безопасно обработать путь к шаблону
                        try:
                            filename = safe_join(zone_templates_dir, f.template_filename)
                        # путь не валидно закодирован в utf-8, путь указан вне базовой директории
                        # ситуация та же, что и при отсутствии шаблона
                        except (UnicodeDecodeError, ValueError) as e:
                            print e
                            continue
                        file = open(filename)
                        try:
                            template_data = file.read().decode(settings.FILE_CHARSET)
                            content = u'{} {} {}'.format(
                                only_for_superuser_text_pre,
                                template_data,
                                only_for_superuser_text_post
                            )
                            source.append(content)
                            dirs.append(filename)
                        finally:
                            file.close()
                    except IOError:
                        # шаблона нет, но ошибку вызывать не стоит, иначе страница
                        # не отобразится, вместо этого просто игнорировать отсутствующий
                        # шаблон
                        pass
                        # error_msg = "Template %s does not exist" % f.template_filename
                        # raise TemplateDoesNotExist(error_msg)

            source_text = ''.join(source)
            dirs_text = ''.join(dirs)
            cache.set(cache_key, {'source': source_text, 'dirs': dirs_text})
            return source_text, dirs_text

_loader = Loader()
