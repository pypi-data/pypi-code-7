import json
import time

from celery import Celery
from django.conf.urls import include, url
from django.test.client import Client
import pytest

from tastypie_celery_resource import TaskResource

@pytest.fixture
def eager_celery_app():
    app = Celery()
    app.conf.update(CELERY_ALWAYS_EAGER=True,
                    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                    BROKER_BACKEND="memory",
                    CELERY_RESULT_BACKEND="cache",
                    CELERY_CACHE_BACKEND="memory")
    return app

@pytest.fixture
def taskadd(eager_celery_app):
    @eager_celery_app.task
    def taskadd(parm1, parm2):
        return parm1+parm2
    return taskadd

@pytest.fixture
def taskadd_resource(taskadd,monkeypatch):

    class TaskAddResource(TaskResource):
        class Meta(TaskResource.Meta):
            task = taskadd
            resource_name = "mytask"

    ret = TaskAddResource()
    import test_urls
    monkeypatch.setattr(test_urls,"urlpatterns",[url('^api/', include(ret.urls))])
    return ret



@pytest.mark.django_db
def test_create(taskadd_resource):

    client = Client()

    resp = client.post("/api/mytask/",json.dumps({'parm1':2,'parm2':3}),content_type="application/json")

    reply = json.loads(resp.content)

    res_url = reply["resource_uri"]

    assert res_url is not None
    assert reply["result"] == 5

@pytest.mark.django_db
def test_get_task(monkeypatch,taskadd,taskadd_resource):
    client = Client()

    class FakeResult:
        def __init__(self,task_id):
            self.task_id = task_id
            self.status = None
            self.result = 5
        def ready(self):
            return True
        def get(self):
            return 5
    def _myAsyncResult(pk):
        if pk == "abcdef12345":
            return FakeResult(pk)
        raise Exception("unexpected pk=%s"%pk)

    monkeypatch.setattr(taskadd,"AsyncResult",_myAsyncResult)


    resp = client.get("/api/mytask/abcdef12345/")
    assert resp.status_code in [ 200, 301 ]
    reply = json.loads(resp.content)
    assert reply["ready"] #it's eagerload, so it's ready for sure
    assert reply["result"] == 5 #2+3
    assert reply["progress"] is None

    #check if is stored in session
    assert client.session["tastypieresource_call_dict"]["mytask"]["abcdef12345"]["result"] == 5

@pytest.mark.django_db
def test_get_progress(monkeypatch,taskadd,taskadd_resource):
    client = Client()

    class FakeResult:
        def __init__(self,task_id):
            self.task_id = task_id
            self.status = "WIP"
            self.result = {"hello":"world","foo":"bar"}
        def ready(self):
            return False
        def get(self):
            assert False #shouldn't be reached

    def _myAsyncResult(pk):
        if pk == "abcdef12345":
            return FakeResult(pk)
        raise Exception("unexpected pk=%s"%pk)

    monkeypatch.setattr(taskadd,"AsyncResult",_myAsyncResult)


    resp = client.get("/api/mytask/abcdef12345/")
    assert resp.status_code in [ 200, 301 ]
    reply = json.loads(resp.content)
    assert reply["ready"] == False
    assert reply["status"] == "WIP"
    assert reply["progress"] == {"hello":"world","foo":"bar"}

@pytest.mark.parametrize("noeager",[True,False])
@pytest.mark.django_db
def test_list_of_called_orders(monkeypatch,eager_celery_app,taskadd_resource,noeager):
    """
        check if you can see list of called orders in GET /api/mytask/
    """

    if noeager:
        monkeypatch.setattr(eager_celery_app.conf,'CELERY_ALWAYS_EAGER',False)

    client = Client()
    task1 = json.loads(client.post("/api/mytask/",json.dumps({'parm1':2,'parm2':3}),content_type="application/json").content)
    task2 = json.loads(client.post("/api/mytask/",json.dumps({'parm1':3,'parm2':4}),content_type="application/json").content)

    sess = client.session

    assert task1["id"] in client.session["tastypieresource_call_dict"]["mytask"]
    assert task2["id"] in client.session["tastypieresource_call_dict"]["mytask"]

@pytest.mark.django_db
def test_return_list_from_dict_in_sess(taskadd_resource):

    client = Client()
    client.get("/api/mytask/") #to initialize cookies etc...
    sess = client.session
    sess["tastypieresource_call_dict"] = {'mytask':{'1234':{'id':'1234'},
                                                              '2345':{'id':'2345'}}}
    sess.save()
    resp = client.get("/api/mytask/")
    ret = json.loads(resp.content)
    assert len(ret["objects"]) == 2
    assert ret["objects"][0]["id"] == "1234"
    assert ret["objects"][1]["id"] == "2345"


@pytest.fixture
def shortliving_taskadd_resource(taskadd,monkeypatch):

    class SlTaskAddResource(TaskResource):
        class Meta(TaskResource.Meta):
            task = taskadd
            resource_name = "mytask"
            keep_seconds = 1

    ret = SlTaskAddResource()
    import test_urls
    monkeypatch.setattr(test_urls,"urlpatterns",[url('^api/', include(ret.urls))])
    return ret

@pytest.mark.django_db
def test_list_of_processed_orders_after_x_secs(shortliving_taskadd_resource):
    """
        check if processed order is NOT in list of GET /api/mytask/ after X seconds from being processed
    """

    client = Client()
    client.post("/api/mytask/",json.dumps({'parm1':2,'parm2':3}),content_type="application/json")
    client.post("/api/mytask/",json.dumps({'parm1':3,'parm2':4}),content_type="application/json")

    client.get("/api/mytask/") #this one should set timestamps
    time.sleep(2)
    resp = client.get("/api/mytask/") #this one purge outdated results
    ret = json.loads(resp.content)
    assert len(ret["objects"]) == 0

@pytest.mark.django_db
def test_if_result_is_stored_in_sess(taskadd_resource):
    client = Client()
    client.post("/api/mytask/",json.dumps({'parm1':2,'parm2':3}),content_type="application/json")
    task_id = json.loads(client.get("/api/mytask/").content)["objects"][0]["id"]

    assert client.session["tastypieresource_call_dict"]["mytask"][task_id]["result"] == 5


def test_no_session_avail(taskadd_resource,monkeypatch):
    """
        what if there is no session in django? should reply empty result
    """
    from django.conf import settings
    monkeypatch.setattr(settings,"INSTALLED_APPS",set(settings.INSTALLED_APPS) - set(['django.contrib.sessions']))
    monkeypatch.setattr(settings,"MIDDLEWARE_CLASSES", set(settings.MIDDLEWARE_CLASSES) - set(['django.contrib.sessions.middleware.SessionMiddleware']))

    #should throw no error
    client = Client()
    client.post("/api/mytask/",json.dumps({'parm1':2,'parm2':3}),content_type="application/json")
    resp = client.get("/api/mytask/")
    ret = json.loads(resp.content)
    assert len(ret["objects"]) == 0



# def test_yeld_in_progress(eager_celery_app, taskadd, monkeypatch):
#     @eager_celery_app.task
#     def yieldtask():
#         print "dupa"
#         yield 1
#         yield 2
#         yield 2
#
#     class YTaskResource(TaskResource):
#         class Meta(TaskResource.Meta):
#             task = yieldtask
#             resource_name = "ytask"
#     ret = YTaskResource()
#     import test_urls
#     monkeypatch.setattr(test_urls,"urlpatterns",[url('^api/', include(ret.urls))])
#
#     client = Client()
#     resp = client.post("/api/ytask/",content_type='application/json')
#     reply = json.loads(resp.content)
#     assert reply is None #FAKE , for debugging sake
