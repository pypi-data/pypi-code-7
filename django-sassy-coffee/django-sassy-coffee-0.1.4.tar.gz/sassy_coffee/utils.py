from django.conf import settings
import os, fnmatch, codecs, sassy_coffee

STATIC_ROOT = os.path.join(sassy_coffee.DJANGO_PATH, 'static')

if(hasattr('settings', 'STATIC_ROOT')):
    STATIC_ROOT = settings.STATIC_ROOT

def locate_folders_to_monitor(format):
    matches = list()
    for root, dirnames, filenames in os.walk(STATIC_ROOT):
        for filename in fnmatch.filter(filenames, format):
            matches.append(root)
            matches.append(os.path.join(root, filename))
    return list(set(matches))

def locate_files_to_compile(format, exclusions=list()):
    matches = list()
    for root, dirnames, filenames in os.walk(STATIC_ROOT):
        for filename in fnmatch.filter(filenames, format):
            base = os.path.splitext(filename)[0]
            if filename not in exclusions and base not in exclusions:
                matches.append((root, os.path.join(root, filename), base))
    return matches

def write_to_file(format, name, path, content):
    if not os.path.exists(os.path.join(os.path.dirname(path), format)):
        os.mkdir(os.path.join(os.path.dirname(path), format))
    dest_f = codecs.open(os.path.join(os.path.dirname(path), '{0}/{1}.{0}'.format(format, name)), mode='w', encoding='utf-8')
    dest_f.write(content)
    dest_f.close()
