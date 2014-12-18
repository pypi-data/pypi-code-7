from collections import defaultdict
from contextlib import contextmanager
import time

from tastypie.resources import Resource, Bundle

@contextmanager
def ctxglob(**kwargs):
    for x,v in kwargs.iteritems():
        setattr(ctxglob,x,v)
    yield
    for x in kwargs.iterkeys():
        delattr(ctxglob,x)

class TaskResource(Resource):

    class Meta:
        always_return_data = True
        keep_seconds = 300 #remember ready results for 5 minutes after they are retrieved

#    def get_resource_uri(self,bundle_or_obj):
    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.task_id
        else:
            kwargs['pk'] = bundle_or_obj.task_id

        return kwargs

    def obj_create(self, bundle, **kwargs):
        taskargs = bundle.data.copy() or {}
        taskargs["request"]=bundle.request
        taskargs = self.modify_args(**taskargs)
        bundle.obj = self._meta.task.delay(**taskargs)

        with ctxglob(request=bundle.request):
            #import pudb;pudb.set_trace()
            self._set_session_item(bundle.obj.task_id,bundle.data)
            return bundle

    def obj_get(self,request=None,**kwargs):
        result = self._meta.task.AsyncResult(kwargs["pk"])
        return result

    def obj_get_list(self, bundle, **kwargs):
        with ctxglob(request=bundle.request):
            self._clean_old_results()
            call_list = []        
            for x,v in self._get_session_items().items():
                call_list.append(self._meta.task.AsyncResult(x))
            return call_list

    def full_dehydrate(self,bundle,for_list=False):
        result = bundle.obj
        with ctxglob(request=bundle.request):
            sess_data = self._get_session_item(result.task_id)
            bundle.data["ready"] = False
            bundle.data["status"] = result.status
            bundle.data["progress"] = result.result
            bundle.data["id"] = result.task_id
            if result.ready():
                bundle.data["ready"] = True
                bundle.data["progress"] = None
                try:
                    bundle.data["result"] = sess_data.get("result",result.get())
                except Exception,e:
                    bundle.data["error"] = "%s"%e

                if not sess_data.get("shown_at",False):
                    sess_data["shown_at"] = time.time()
                
                self._set_session_item(result.task_id,bundle.data)
        return super(TaskResource,self).full_dehydrate(bundle)

    # def full_dehydrate_list(self,bundle):
    #     call_list = bundle

    def modify_args(self,request,**kwargs):
        return kwargs

    def _get_session_items(self):
        request = ctxglob.request
        if not hasattr(request,"session"): #no session support?
            return {}
        session = request.session
        calldict = session.setdefault("tastypieresource_call_dict",{})
        calls_for_task = calldict.setdefault(self._meta.resource_name,{})
        return calls_for_task

    def _commit_session(self):
        request = ctxglob.request
        if not hasattr(request,"session"): #no session support?
            return
        request.session.modified = True

    def _get_session_item(self,task_id):
        calldict = self._get_session_items()
        sess_data = calldict.setdefault(task_id,{'id':task_id})
        return sess_data

    def _set_session_item(self,task_id,sess_data):
        calldict = self._get_session_items()
        calldict[task_id] = sess_data
        self._commit_session()

    def _clean_old_results(self):
        sess = self._get_session_items()
        for k,v in sess.items():
            sat = v.get("shown_at")
            if sat:
                if time.time() - sat > self._meta.keep_seconds:
                    del(sess[k])
        self._commit_session()
        
