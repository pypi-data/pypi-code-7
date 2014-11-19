# -*- coding: utf-8 -*-

from django.template import Library

from meringue.utils.thumbnails import get_thumbnail


register = Library()


@register.filter
def thumbnail(filename, args=''):
    '''
        Фильтр обработки изображений, применяется к локальнуму адресу
    изображения (путь до файла) в аргументах ожидает параметры изменения
    изображения разделённые запятой, последовательность действий соответствует
    последовательности введённых аргументов т.е. последовательность -
    s:600x400,resize,s:400x400,crop - сначала задас целевой размер изображения
    600x400, далее скукожит (или растянет изображение в зависимости от
    исходного и других параметров) до 600x400, потом установит новый целевой
    размер 400x400 и отрежет лишнее.

    Аргументы фильтра:
        s:<width>x<height> - указывает целевой размер изображения для
            последующий фенуций
        crop - изменения размера холста до последнего установленного
        resize - изменение размера изображения до последнего установленного
        q:<quality> - укажет качество конечного изображения 0-100
            (используется в последний момент при сохранении)
        c:<color> - цвет заливки для кропа в формате rgba
            (c:255 255 255 255)
        rm:scale|inscribe|stretch - метод ресайза вписать в размер или
            растянуть
        cm:left|center|rigth top|center|bottom - точка отсчёта для кропа

    TO-DO:
        watermark
        определение лица и использование в роли центра изображения
        указание максимальной ширины или высоты
        определение фокуса
    '''

    task_list = args.split(',')
    return get_thumbnail(filename=filename, task_list=task_list)
