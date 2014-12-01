from django.contrib import admin
from Deploymentapp.models import Hosts,Users,Task,Commands

# Register your models here.
class AdministratorHosts(admin.ModelAdmin):
	#prepopulated_fields = {'Id_task' : ('Id_task',)}
	list_display = ('idhosts','hostname','basepath')
admin.site.register(Hosts,AdministratorHosts)

class AdministratorUsers(admin.ModelAdmin):
	#prepopulated_fields = {'Id_task' : ('Id_task',)}
	list_display = ('iduser','usersname')
admin.site.register(Users,AdministratorUsers)

class AdministratorTask(admin.ModelAdmin):
	#prepopulated_fields = {'Id_task' : ('Id_task',)}
	list_display = ('idtask','author','taskname','status')
admin.site.register(Task,AdministratorTask)

class AdministratorCommands(admin.ModelAdmin):
	#prepopulated_fields = {'Id_task' : ('Id_task',)}
	list_display = ('idtasks','commandname','parameter1','parameter2')
admin.site.register(Commands,AdministratorCommands)