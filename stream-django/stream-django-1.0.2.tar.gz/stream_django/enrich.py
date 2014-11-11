import collections
from collections import defaultdict
from django.db.models.loading import get_model
import operator
import itertools


def combine_dicts(a, b, op=operator.add):
    return dict(a.items() + b.items() +
        [(k, op(a[k], b[k])) for k in set(b) & set(a)])


DEFAULT_FIELDS = ('actor', 'object')


class EnrichedActivity(collections.MutableMapping):

    def __init__(self, activity_data):
        self.activity_data = activity_data
        self.not_enriched_fields = []

    def __getitem__(self, key):
        return self.activity_data[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.activity_data[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.activity_data[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.activity_data)

    def __len__(self):
        return len(self.activity_data)

    def __keytransform__(self, key):
        return key

    def track_not_enriched_fields(self, field):
        self.not_enriched_fields.append(field)

    def enriched(self):
        len(self.not_enriched_fields) == 0


class Enrich(object):

    def __init__(self, fields=DEFAULT_FIELDS):
        self.fields = fields

    def enrich_aggregated_activities(self, activities):
        references = {}
        for activity in activities:
            activity['activities'] = self.wrap_activities(activity['activities'])
            references = combine_dicts(references, self._collect_references(activity['activities'], self.fields))
        objects = self._fetch_objects(references)
        for activity in activities:
            self._inject_objects(activity['activities'], objects, self.fields)
        return activities

    def enrich_activities(self, activities):
        activities = self.wrap_activities(activities)
        references = self._collect_references(activities, self.fields)
        objects = self._fetch_objects(references)
        self._inject_objects(activities, objects, self.fields)
        return activities

    def wrap_activities(self, activities):
        return [EnrichedActivity(a) for a in activities]

    def is_ref(self, activity, field):
        return (activity.get('field', '').split(':') == 2)

    def _collect_references(self, activities, fields):
        model_references = defaultdict(list)
        for activity, field in itertools.product(activities, fields):
            if self.is_ref(activity, field):
                continue
            f_ct, f_id = activity[field].split(':')
            model_references[f_ct].append(f_id)
        return model_references

    def fetch_model_instances(self, modelClass, pks):
        '''
        returns a dict {id:modelInstance} with instances of model modelClass
        and pk in pks
        '''
        hook_function_name = 'fetch_%s_instances' % (modelClass._meta.object_name.lower(), )
        if hasattr(self, hook_function_name):
            return getattr(self, hook_function_name)(pks)
        qs = modelClass.objects
        if hasattr(modelClass, 'related_models') and modelClass.related_models() is not None:
            qs = qs.select_related(*modelClass.related_models())
        return qs.in_bulk(pks)

    def _fetch_objects(self, references):
        objects = defaultdict(list)
        for content_type, ids in references.items():
            model = get_model(*content_type.split('.'))
            ids = set(ids)
            instances = self.fetch_model_instances(model, ids)
            objects[content_type] = instances
        return objects

    def _inject_objects(self, activities, objects, fields):
        not_enriched = []
        for activity, field in itertools.product(activities, fields):
            if not self.is_ref(activity, field):
                continue
            f_ct, f_id = activity[field].split(':')
            instance = objects[f_ct].get(int(f_id))
            if instance is None:
                not_enriched.append(activity, field)
            else:
                activity[field] = instance

        for activity, field in not_enriched:
            activity.track_not_enriched_fields(field)
