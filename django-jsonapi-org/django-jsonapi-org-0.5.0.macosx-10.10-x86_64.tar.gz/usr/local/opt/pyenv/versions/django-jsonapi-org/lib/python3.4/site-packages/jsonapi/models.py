# encoding=utf-8
import re
from jsonapi import JSONAPI
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models.base import Model
from django.core.paginator import Paginator


class ModelJSONAPI(JSONAPI):

    model = None
    model_name = None
    
    filters = ()
    order_fields = ()

    def __init__(self):
        # モデル名をModelクラスから自動生成する
        if not self.model_name:
            self.model_name = self.model.__name__.lower() + "s"  # FIXME:正しい複数形を生成する
        super(ModelJSONAPI, self).__init__()


    """リクエスト処理関係"""

    def get_change_form(self, request, item, data):
        FormClass = self.change_form
        return FormClass(data, instance=item)

    """シリアライズ関係"""
    def json_serialize(self, obj):
        """JSONに変換できないオブジェクトを変換"""
        if isinstance(obj,Model):
            return obj.id
        return super(ModelJSONAPI,self).json_serialize(obj)
    
    def response(self, data):
        if settings.DEBUG == True:
            from django.db import connection
            self.metadata["queries"] = connection.queries
        return super(ModelJSONAPI,self).response(data)

    """データ取得処理関係"""
    def get_queryset(self, request):
        return self.model.objects.all()

    def get_items_for_request(self, request):
        queryset = self.get_queryset(request)
        
        # フィルタリング
        filter_dict = {}
        for f in self.filters:
            if isinstance(f,(list,tuple)):
                attr = f[0]
                field = f[1]
            else:
                attr = field = f
            
            value = request.GET.get(attr)
            if value:
                filter_dict[field] = value
        queryset = queryset.filter(**filter_dict)
        
        # ソート
        order_fields_dict = {}
        for f in self.order_fields:
            if isinstance(f,(list,tuple)):
                attr = f[0]
                field = f[1]
            else:
                attr = field = f
            order_fields_dict[attr] = field
        
        order_by_list = []
        sorts = request.GET.getlist("sort")
        sort_re = re.compile("^([+-]?)(.+)$")
        for sort in sorts:
            match = sort_re.match(sort)
            if match:
                order, attr = match.groups()
                if attr in order_fields_dict:
                    field = order_fields_dict[attr]
                    if order == "-":
                        field = "-" + field
                    order_by_list.append(field)

        if order_by_list:
            queryset = queryset.order_by(*order_by_list)
        
        
        # ページネーション
        per_page = 0
        page = 1
        try:
            per_page = int(request.GET.get("per_page","0"))
            page = int(request.GET.get("page","1"))
        except ValueError:
            pass
        if per_page > 0:
            paginator = Paginator(queryset,per_page)
            if page not in paginator.page_range:
                page = 1
            page = paginator.page(page)
            queryset = page.object_list
            self.metadata.update({
                                  "total":paginator.count,
                                  "per_page":per_page,
                                  "page":page.number
                                  })
        return queryset

    def get_item_by_id(self, request, id):
        return get_object_or_404(self.get_queryset(request), id=id)

    """データ更新関係"""
    def process_add_items(self, request, forms):
        items = []
        for form in forms:
            items.append(form.save())
        return items

    def process_update_item(self, request, form):
        item = form.save()
        return item

    def process_delete_item(self, request, item):
        item.delete()
        return None


