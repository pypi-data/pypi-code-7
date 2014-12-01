from django.db import models

# Create your models here.
class DjangoApp(models.Model) :
	buttonName = models.TextField()
	slug = models.SlugField()
	command = models.TextField()
	@models.permalink
	def get_link(self):
		return('app', [self.slug])
	def name(self):
		return self.buttonName