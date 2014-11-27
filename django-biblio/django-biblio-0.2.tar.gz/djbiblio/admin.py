from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django import forms
from django import http
from djbiblio import models
from conf.settings import MEDIA_URL

import bibtexparser as bp
import urlparse     as up

def work_bibdict(obj):
    bibtags = obj.bibtags.all()
    d = { b.tag : b.value for b in bibtags }
    return d

def export_bibtex(modeladmin, request, queryset, file='biblio'):
    db     = bp.bibdatabase.BibDatabase()
    writer = bp.bwriter.BibTexWriter()
    for obj in queryset:
        db.entries.append(work_bibdict(obj))
    response = http.HttpResponse(content_type='application/x-bibtex')
    response['Content-Disposition'] = 'attachment; filename=%s.bib' % file
    writer.comma_first = True
    response.write(writer.write(db))
    return response
export_bibtex.short_description = u'Export as BibTeX'

def export_project(modeladmin, request, queryset):
    prj = queryset[0].slug
    qs  = reduce( lambda x,y: x | y.works.all()
                , queryset, models.Work.objects.none() )
    return export_bibtex(modeladmin, request, qs.distinct(), prj)
export_project.short_description = u'Export as BibTeX'

class ProjectAdmin(admin.ModelAdmin):
    actions = [ export_project ]
    readonly_fields = ['no_works']
    fields          = [ [ 'name' , 'slug' ] ]
    list_display    =   [ 'name' , 'slug' , 'no_works']
    search_fields   =   [ 'name' , 'slug' ]
    def no_works(self, inst):
        return inst.works.count()
    no_works.allow_tags        = True
    no_works.short_description = u' Number of papers'
admin.site.register(models.Project, ProjectAdmin)

class BibtagForm(forms.ModelForm):
    tag   = forms.CharField( max_length=20
                           , widget=forms.TextInput(attrs={'size':20}) )
    value = forms.CharField( max_length=1000
                           , widget=forms.TextInput(attrs={'size':70}) )
    class Meta:
        model  = models.Bibtag
        fields = [ 'tag' , 'value' ]
        #exclude = [ 'works' ]

class BibtagAdmin(admin.TabularInline):
    model = models.Bibtag
    form  = BibtagForm
#admin.site.register(models.Bibtag, BibtagAdmin)

#class AuthorAdmin(admin.StackedInline):
#    model = models.Author.works.through
#admin.site.register(models.Author, AuthorAdmin)

tarea = forms.Textarea(attrs={'rows':12,'cols':70})

class WorkForm(forms.ModelForm):
    mnemonic = forms.CharField( max_length=120
                              , widget=forms.TextInput(attrs={'size':70}) )
    slug     = forms.SlugField(max_length=30)
    abstract = forms.CharField(max_length=2000, required=False, widget=tarea)
    bibtex   = forms.CharField(max_length=3000, required=False, widget=tarea)
    workurl  = forms.URLField( label="Work's URL"
                             , required=False
                             , widget=forms.TextInput(attrs={'size':70}) )
    upload   = forms.FileField(max_length=80, required=False)
    def clean_slug(self):
        if self.obj:  # this is a change, don't bother checking uniqueness
            return self.cleaned_data['slug']
        try:
            models.Work.objects.get(slug=self.cleaned_data['slug'])
        except models.Work.DoesNotExist:
            return self.cleaned_data['slug']
        dups = 'This slug already exist, you must choose a different one'
        raise forms.ValidationError(dups, code='duplicatedworkslug')
    def clean(self):
        if not 'slug' in self.cleaned_data:  # bail
            return self.cleaned_data
        if self.cleaned_data.get('upload', False):
            url = ( 'http://' + get_current_site(self.req).domain + MEDIA_URL
                  + models.upload_work( self.cleaned_data['slug']
                                      , self.cleaned_data['upload'].name ) )
            self.cleaned_data['workurl'] = url
        if not self.cleaned_data.get('workurl', False):
            raise forms.ValidationError( 'You must provide a URL or a file'
                                       , code='urlfile' )
        return self.cleaned_data
    def save(self, *args, **kwargs):
        work = super(WorkForm, self).save(*args, **kwargs)
        work.save()
        self.save_m2m()
        records = bp.loads(self.cleaned_data['bibtex'])
        if records.entries:
            en = records.entries[0]
            if not en.get('type', False): en['type'] = 'misc'
        else:
            en = {}
            en['type'] = 'misc'
        en['id'] = self.cleaned_data['slug']
        for r in en.keys():
            try:  # it is there, so it is in the inline
                models.Bibtag.objects.get(tag=r, work=work)
            except models.Bibtag.DoesNotExist:
                models.Bibtag.objects.create(tag=r, value=en[r], work=work)
        return work
    class Meta:
        model   = models.Work
        fields  = [ 'mnemonic' , 'slug'
                  , 'projects' , 'abstract'
                  , 'workurl'  , 'upload'
                  , 'bibtex'
                  ]
        #exclude = ['projects']

class LocalFileFilter(admin.SimpleListFilter):
    title          = 'paper location'
    parameter_name = 'local'
    def lookups(self, request, model_admin):
        return (
            ( 'local'  , 'local files'  ),
            ( 'remote' , 'remote files' ),
               )
    def queryset(self, request, queryset):
        if self.value() == 'local':
            return queryset.exclude(upload='')
        if self.value() == 'remote':
            return queryset.filter(upload='')
        return queryset

class WorkAdmin(admin.ModelAdmin):
    actions = [ export_bibtex ]
    inlines = [ BibtagAdmin ] # , AuthorAdmin ]
    form    = WorkForm
    readonly_fields = ['show_url']
    fields  = [ [ 'mnemonic' , 'slug'     ]
              , [ 'projects' , 'abstract' ]
              , [ 'workurl'  , 'show_url' ]
              , 'upload'
              , 'bibtex'
              ]
    list_filter   = [ LocalFileFilter ]
    list_display  = [ 'mnemonic' , 'slug', 'show_url' ]
    search_fields = [ 'mnemonic' , 'slug', 'abstract' ]
    def get_form(self, request, obj=None, **kwargs):
        form = super(WorkAdmin, self).get_form(request, obj, **kwargs)
        form.req = request
        form.obj = obj
        return form
    def show_url(self, inst):
        purl   = up.urlparse(inst.workurl)
        domain = '{uri.netloc}'.format(uri=purl)
        return '<a href="%s" target="_blank">%s</a>' % (inst.workurl , domain)
    show_url.allow_tags        = True
    show_url.short_description = u'View paper'
admin.site.register(models.Work, WorkAdmin)

