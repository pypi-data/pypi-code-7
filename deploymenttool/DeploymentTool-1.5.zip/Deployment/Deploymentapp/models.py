from django.db import models

# Create your models here.
class Hosts (models.Model):
	idhosts = models.AutoField(primary_key = True)
	hostname = models.IPAddressField()
	username = models.CharField(max_length = 25)
	passwd = models.CharField(max_length = 125)
	basepath = models.CharField(max_length = 250)

class Users(models.Model):
	iduser = models.AutoField(primary_key = True)
	usersname = models.CharField(max_length = 25)
	host = models.ForeignKey(Hosts)
	basepaths = models.CharField(max_length = 250)

class Task(models.Model):
	idtask = models.AutoField(primary_key = True)
	author = models.ForeignKey(Users)
	taskname = models.CharField(max_length = 25)
	hostes = models.ForeignKey(Hosts)
	status = models.BooleanField()
	basespath = models.CharField(max_length = 250)
	@models.permalink
	def get_absolute_url(self) :
		return ('tasklist',[self.idtask])
	def get_url_path(self):
		return '/deletetask/%s' % self.idtask
	def get_url_revert(self):
		return '/dorevert/%s' % self.idtask
	def __unicode__(self):
		return self.taskname
	class Meta :
		ordering = ['-taskname']
		
class Commands(models.Model):
	idtasks = models.ForeignKey(Task)
	idcommand = models.AutoField(primary_key = True)
	commandname= models.CharField(max_length = 25)
	parameter1 = models.CharField (max_length = 30)
	parameter2 = models.CharField(max_length = 30)
	hostetes = models.ForeignKey(Hosts)
	basespaths = models.CharField(max_length = 250)
	alias = models.CharField (max_length = 50)
	isdefault = models.BooleanField()
	localbasepath = models.CharField (max_length = 250)
	@models.permalink
	def get_absolute_url(self) :
		return ('editcommand',[self.idcommand])
	def get_url_path(self):
		return '/deletecommand/%s' % self.idcommand
	def url_edit_command(self):
		return '/editcommand/%s' % self.idcommand
	def __unicode__(self):
		return self.idcommand
	class Meta :
		ordering = ['-idcommand']