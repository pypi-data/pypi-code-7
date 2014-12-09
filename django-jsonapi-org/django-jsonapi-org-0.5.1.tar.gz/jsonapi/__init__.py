# encoding=utf-8
from collections import OrderedDict, Iterable
from functools import update_wrapper
import json

from django.db.models.query import QuerySet
from django.http.response import HttpResponseNotAllowed, HttpResponse, Http404, \
    HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt


class JSONAPI(object):

    model_name = "model"

    fields = ("id",)

    add_form = None
    change_form = None

    content_type = "application/json"

    metadata = {}

    def wrap_view(self, view_func):
        return csrf_exempt(view_func)

    def get_urls(self):
        from django.conf.urls import patterns, url

        urlpatterns = patterns('',
            url(r'^$',
                self.wrap_view(self.request_index),
                name='%s_index' % self.model_name),
            url(r'^(.+)/$',
                self.wrap_view(self.request_item),
                name='%s_item' % self.model_name),
        )
        return urlpatterns

    def urls(self):
        return self.get_urls()
    urls = property(urls)

    """リクエストの処理関係"""

    def request_index(self, request):
        if request.method == "GET":
            return self.get_index(request)
        if request.method == "POST":
            # ADD
            return self.post_index(request)
        return HttpResponseNotAllowed("")

    def request_item(self, request, id):
        if request.method == "GET":
            return self.get_item(request, id)
        if request.method == "PUT":
            return self.put_item(request, id)
        if request.method == "DELETE":
            return self.delete_item(request, id)
        return HttpResponseNotAllowed("")


    # 取得系
    def get_index(self, request):
        items = self.get_items_for_request(request)
        return self.response(self._items_to_dict(items))

    def get_item(self, request, id):
        item = self.get_item_by_id(request, id)
        if item is None:
            raise Http404()
        return self.response(self._items_to_dict(item))

    # ADD
    def post_index(self, request):

        if self.add_form is None:
            # フォームが用意されていない場合には追加できない
            return HttpResponseNotAllowed("")

        payload = self._get_json_payload(request)
        if payload is None or self.model_name not in payload:
            return HttpResponseBadRequest("Bad struct")

        items_data = payload[self.model_name]

        FormClass = self.add_form

        if not isinstance(items_data, (list, tuple)):
            # 全て配列にしておく
            items_data = [items_data]

        # Formでバリデーションを行う
        forms = []
        all_is_valid = True
        for item_data in items_data:
            form = FormClass(item_data)
            if not form.is_valid():
                all_is_valid = False
            forms.append(form)

        if not all_is_valid:
            # バリデーションエラーレスポンス
            error_list = [form.errors for form in forms]
            response = self.response(error_list)
            response.status_code = 400
            return response

        # 新規登録処理を行う
        items = self.process_add_items(request, forms)
        if isinstance(items, HttpResponse):
            return items  # Generate HttpResponse by "process_add_items"

        # 保存したItemをレスポンスとして返す
        return self.response(self._items_to_dict(items))

    def get_change_form(self, request, item, data):
        FormClass = self.change_form
        return FormClass(data, initial=item)


    def put_item(self, request, id):

        if self.change_form is None:
            # フォームが用意されていない場合には追加できない
            return HttpResponseNotAllowed("")

        payload = self._get_json_payload(request)
        if payload is None or self.model_name not in payload:
            return HttpResponseBadRequest("Bad struct")

        item_data = payload[self.model_name]
        if isinstance(item_data, (list, tuple)):
            return HttpResponseBadRequest("Cannot Multiple Modify")

        # 編集前のオブジェクト
        item = self.get_item_by_id(request, id)
        if item is None:
            raise Http404

        # Formによるバリデーション
        form = self.get_change_form(request, item, item_data)
        if not form.is_valid():
            # バリデーションエラーレスポンス
            response = self.response(form.errors)
            response.status_code = 400
            return response

        item = self.process_update_item(request, form)
        if isinstance(item, HttpResponse):
            return item  # Generete HttResponse by "process_update_item"

        # 生成されたItemを結果として返す
        return self.response(self._items_to_dict(item))

    def delete_item(self, request, id):
        # 削除前のオブジェクト
        item = self.get_item_by_id(request, id)
        if item is None:
            raise Http404

        response = self.process_delete_item(request, item)
        if response is None:
            response = HttpResponse(status=202)  # Accepted
        return response

    def _get_json_payload(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return None
        return payload


    """シリアライズ処理"""
    def _items_to_dict(self, items):
        d = OrderedDict()
        if isinstance(items, (list, tuple, QuerySet)):
            d[self.model_name] = []
            for item in items:
                d[self.model_name].append(self._item_to_dict(item))
        else:
            item = items
            d[self.model_name] = self._item_to_dict(item)
        return d

    def _getattr(self, item, name):
        value = item
        # 再帰的に値を参照する
        for f in name.split("__"):
            try:
                value = getattr(value, f)
            except AttributeError:
                value = value[f]

            if callable(value):
                # 関数オブジェクトであれば結果を用いる
                value = value()
        return value

    def _item_to_dict(self, item):
        d = OrderedDict()
        for field in self.fields:
            value = item
            if isinstance(field, (list, tuple)):
                # ("json_attr_name", "item_attr")
                field_name = field[0]
                field = field[1]
            else:
                field_name = field

            d[field_name] = self._getattr(value, field)

        return d

    def response(self, data):
        if self.metadata and isinstance(data, dict):
            data["meta"] = self.metadata
        response = HttpResponse(json.dumps(data, default=self.json_serialize),
                                content_type=self.content_type)
        return response

    def json_serialize(self, obj):
        """JSONに変換できないオブジェクトを変換"""
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        raise ValueError

    """データ更新関係"""
    def process_add_items(self, request, forms):
        items = []
        for form in forms:
            items.append(form.cleaned_data)
        return items

    def process_update_item(self, request, form):
        item = form.cleaned_data
        return item

    def process_delete_item(self, request, item):
        return None

    """データの取得関係"""
    def id_to_python(self, id_str):
        return int(id_str)

    def get_items_for_request(self, request):
        """すべてのデータを返すメソッド"""
        raise NotImplementedError

    def get_item_by_id(self, request, id):
        """IDで特定のデータを返すメソッド"""
        id = self.id_to_python(id)
        for item in self.get_items_for_request(request):
            if self._getattr(item, "id") == id:
                return item
        return None


