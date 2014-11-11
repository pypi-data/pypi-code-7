from django.db.models.signals import post_save
import os
import uuid


def get_model_field_by_name(model, name):
	"""
	Same as model.get_field_by_name(name)[0], but doesn't trigger django.db.models.loading._populate and thus prevents circular imports in some cases
	"""
	return filter(lambda f: f.name==name, model._meta.fields)[0]


def upload_to_uuid(path, make_dir=False):
	import sys
	if len(sys.argv) > 1 and sys.argv[1] in ('makemigrations', 'migrate'):
		return None # Hide ourselves from Django migrations

	def generate_filename(instance, filename):
		unused, ext = os.path.splitext(filename)
		basename = uuid.uuid4().urn.split(':')[-1]
		if make_dir:
			return os.path.join(path, basename, filename.replace(' ', '_'))
		else:
			return os.path.join(path, basename + ext.lower())
	return generate_filename


def reload_object(obj):
	obj.__dict__ = obj.__class__.objects.get(pk=obj.pk).__dict__


def lock_object(obj):
	if not hasattr(obj, '_locked'):
		obj.__dict__ = obj.__class__.objects.select_for_update().get(pk=obj.pk).__dict__
		obj._locked = True


def update_object(obj, reload=False, signal=True, **kwargs):
	updated = obj.__class__.objects.filter(pk=obj.pk).update(**kwargs) > 0
	if reload:
		reload_object(obj)
	else:
		for k, v in kwargs.items():
			setattr(obj, k, v)
	if updated and signal:
		post_save.send(sender=obj.__class__, instance=obj, created=False)
	return updated
