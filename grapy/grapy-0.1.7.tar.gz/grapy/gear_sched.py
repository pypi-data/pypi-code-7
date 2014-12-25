import gear
from .core import Request, BaseScheduler, dump_item, load_item
from .utils import logger
import copy
import aiogear
from .core.exceptions import IgnoreRequest, DropItem, RetryRequest, ItemError

__all__ = ['GearScheduler']

class GearScheduler(BaseScheduler):
    def __init__(self, **options):
        self._client = gear.Client()
        self._worker = aiogear.Worker(options.get('MAX_REQUEST', 5)) # base on aiogear
        self.options = options

        self._funcs = []
        for gearman_server in options['GEARMAN_SERVERS']:
            self._client.addServer(*gearman_server)
            self._funcs.append(self._worker.add_server(*gearman_server))
        self._client.waitForServer()  # Wait for at least one server to be connected

        is_pipe = True
        is_req = True
        if self.options.get('ONLY_REQ') or self.options.get('ONLY_PIPE'):
            if self.options.get('ONLY_REQ'):
                is_pipe = False
            else:
                is_req = False

        if is_req:
            self.register('process_req', self.process_req)

        if is_pipe:
            self.register('process_pipeline', self.process_pipeline)

    def _get_func_name(self, func_name):
        return '{}_{}'.format(self.options.get('REQUEST_TYPE', ''), func_name)

    def submit(self, func, data, background=True, precedence=0):
        logger.debug('submit: ' + func + str(data))
        job = gear.Job(self._get_func_name(func), data)
        self._client.submitJob(job, background, precedence)

    def register(self, func_name, func):
        logger.debug('register: ' + func_name)
        func_name = self._get_func_name(func_name)
        self._funcs.append(self._worker.add_func(func_name, func))

    def push_req(self, req):
        if self.options.get('SUBMIT_REQUEST', True):
            self.submit('process_req', bytes(req))

    def push_item(self, item):
        pipelines = filter(lambda x: getattr(x, 'immediate', True),
                copy.copy(self.engine.pipelines))
        yield from self.engine.process_item(item, pipelines)
        if self.options.get('SUBMIT_PIPELINT', True):
            self.submit('process_pipeline', bytes(dump_item(item), 'UTF-8'))

    def process_pipeline(self, job):
        payload = str(job.workload, 'UTF-8')
        item = load_item(payload)
        pipelines = filter(lambda x: not getattr(x, 'immediate', True),
                copy.copy(self.engine.pipelines))
        try:
            yield from self.engine.process_item(item, pipelines)
        except (DropItem, ItemError):
            pass
        except Exception as e:
            logger.exception(e)
        yield from job.complete(b'ok')

    def process_req(self, job):
        payload = job.workload
        req = Request.build(payload)
        retry_times = self.options.get('RETRY_TIMES', 5)
        while retry_times > 0:
            try:
                yield from self.submit_req(req)
                break
            except (IgnoreRequest, DropItem):
                break
            except RetryRequest:
                pass
            except Exception as e:
                logger.exception(e)
                break

            retry_times -= 1

        yield from job.complete(b'ok')

    def run(self):
        for func in self._funcs:
            yield from func
        self._funcs = []

        self._worker.work()
