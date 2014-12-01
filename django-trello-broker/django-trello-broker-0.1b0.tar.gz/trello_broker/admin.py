from django.db.models import Q
from django.contrib import admin
from .forms import BitBucketRepoAdminForm, BitBucketRuleAdminForm
from .models import (
    STATUS_ACTIVE, TrelloToken, TrelloBoard, TrelloList,
    BitBucketRepo, BitBucketRule,
)


class BaseTrelloBrokerAdmin(admin.ModelAdmin):
    exclude = ('created', 'modified')


class TrelloBoardAdmin(BaseTrelloBrokerAdmin):
    actions = ['update_board',]
    list_filter = ('trello_token__name', 'status')

    def update_board(self, request, queryset):
        for board in queryset:
            board.update_from_json()
            board.populate_all_lists()
    update_board.short_description = (
        'Re-populate board & list data from Trello API'
    )


class TrelloListAdmin(BaseTrelloBrokerAdmin):
    list_filter = ('trello_board', 'status')


class BitBucketRuleInline(admin.TabularInline):
    model = BitBucketRule
    form = BitBucketRuleAdminForm

    def get_extra(self, request, obj=None, **kwargs):
        self._max_extra = len(BitBucketRule.ACTION_CHOICES)
        extra = 0
        if obj is not None:
            self._cnt = obj.rules.count()
            if (self._max_extra - self._cnt):
                extra = 1
        self._extra = extra
        return extra

    def get_max_num(self, request, obj=None, **kwargs):
        if self._cnt < self._max_extra:
            return (self._cnt + 1)
        return 0

    def get_formset(self, request, obj=None, **kwargs):
        self._object = obj
        return super(BitBucketRuleInline, self).get_formset(request,  obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'trello_list':
            obj = getattr(self, '_object', None)
            if obj is not None:
                query = Q(trello_board=obj.trello_board) & \
                        Q(status=STATUS_ACTIVE)
                kwargs['queryset'] = TrelloList.objects.filter(query)
        return super(BitBucketRuleInline, self).formfield_for_foreignkey(
            db_field,
            request,
            **kwargs
        )


class BitBucketRepoAdmin(BaseTrelloBrokerAdmin):
    inlines = [BitBucketRuleInline]
    form = BitBucketRepoAdminForm

    def get_formsets_with_inlines(self, request, obj=None):
        if obj is None:
            # No inlines when adding a new object
            return

        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj), inline


admin.site.register(TrelloToken, BaseTrelloBrokerAdmin)
admin.site.register(TrelloBoard, TrelloBoardAdmin)
admin.site.register(TrelloList, TrelloListAdmin)
admin.site.register(BitBucketRepo, BitBucketRepoAdmin)
