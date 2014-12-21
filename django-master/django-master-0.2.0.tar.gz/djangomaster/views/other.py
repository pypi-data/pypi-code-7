import os
from subprocess import Popen
import tempfile

from djangomaster.views import MasterView, MasterJSONView
from djangomaster.conf import settings


class TestView(MasterView):
    template_name = 'djangomaster/test.html'
    menu_item = 'test'

    def get_context_data(self, **kwargs):
        context = super(TestView, self).get_context_data(**kwargs)
        context['cmd'] = self.request.GET.get('cmd', 'test')

        return context

    def get_queryset(self):
        return []


class ExecuteTestView(MasterJSONView):

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super(ExecuteTestView, self).get_context_data(**kwargs)
        context['cmd'] = self.request.GET.get('cmd', 'test')
        file_path = self._execute(context['cmd'])
        context['file'] = os.path.split(file_path)[1]
        return context

    def get_random_file(self):
        _file = tempfile.NamedTemporaryFile(prefix='test', suffix='.txt',
                                            dir=settings.TEST_STATIC_FOLDER,
                                            delete=False)
        return open(_file.name, 'wr')

    def _execute(self, cmd):
        # check this to improvement:
        # http://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
        cmd = ['python', 'manage.py'] + cmd.split(' ')
        f = self.get_random_file()
        Popen(cmd, stdout=f, stderr=f)
        return f.name


class CheckTestView(MasterJSONView):

    def get_queryset(self):
        return []

    def _get_offset(self):
        try:
            return int(self.request.GET.get('offset', 0))
        except ValueError:
            return 0

    def get_context_data(self, **kwargs):
        ctx = super(CheckTestView, self).get_context_data(**kwargs)
        file_path = self.request.GET.get('file', '')
        file_path = os.path.join(settings.TEST_STATIC_FOLDER, file_path)
        offset = self._get_offset()

        try:
            with open(file_path, 'r') as f:
                ctx['output'] = f.read()[offset:]
                ctx['finished'] = 'Destroying test database' in ctx['output']
        except IOError:
            ctx['output'] = 'File doesnt exist'
            ctx['finished'] = True

        return ctx
