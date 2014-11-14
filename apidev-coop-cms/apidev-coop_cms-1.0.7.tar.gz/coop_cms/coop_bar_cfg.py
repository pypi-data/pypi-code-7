# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import Context
from coop_cms.models import Link, Fragment
from coop_cms.settings import get_article_class, get_navtree_class, cms_no_homepage, hide_media_library_menu
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from coop_bar.utils import make_link

def can_do(perm, object_names):
    def inner_decorator(func):
        def wrapper(request, context):
            editable = context.get('editable')
            if not editable:
                return
            for object_name in object_names:
                obj = context.get(object_name, None)
                if obj != None:
                    
                    callback_name = u"coop_cms_{0}_callback".format(perm, object_name)
                    callback = context.get(callback_name, None)
                    
                    if callback and request and callback():
                        yes_we_can = func(request, context)
                        if yes_we_can:
                            return yes_we_can
            return
        return wrapper
    return inner_decorator

can_edit_article = can_do('can_edit', ['article'])
can_edit_object = can_do('can_edit', ['article', 'object', 'objects'])
can_publish_article = can_do('can_publish', ['article'])
can_edit_newsletter = can_do('can_edit', ['newsletter'])
can_edit = can_do('can_edit', ['article', 'newsletter', 'object'])

def can_add_article(func):
    def wrapper(request, context):
        Article = get_article_class()
        ct = ContentType.objects.get_for_model(Article)
        perm = '{0}.add_{1}'.format(ct.app_label, ct.model)
        if request and request.user.has_perm(perm):
            return func(request, context)
        return None
    return wrapper

def can_add_link(func):
    def wrapper(request, context):
        ct = ContentType.objects.get_for_model(Link)
        perm = '{0}.add_{1}'.format(ct.app_label, ct.model)
        if request and request.user.has_perm(perm):
            return func(request, context)
        return None
    return wrapper

def django_admin(request, context):
    if request and request.user.is_staff:
        return make_link(reverse("admin:index"), _(u'Administration'), 'fugue/tables.png',
            classes=['icon', 'alert_on_click'])
        
def django_admin_edit_article(request, context):
    if request and request.user.is_staff and 'article' in context:
        article_class = get_article_class()
        article = context['article']
        view_name = 'admin:%s_%s_change' % (article_class._meta.app_label,  article_class._meta.module_name)
        return make_link(reverse(view_name, args=[article.id]), _(u'Article admin'), 'fugue/table.png',
            classes=['icon', 'alert_on_click'])

def django_admin_edit_object(request, context):
    if request and request.user.is_staff and context.get('object', None):
        obj = context['object']
        object_class = obj.__class__
        view_name = 'admin:%s_%s_change' % (object_class._meta.app_label,  object_class._meta.module_name)
        try:
            return make_link(reverse(view_name, args=[object.id]),
                _(u'Admin {0}'.format(object_class._meta.verbose_name)), 'fugue/table.png',
                classes=['icon', 'alert_on_click'])
        except:
            pass

def django_admin_add_object(request, context):
    if request and request.user.is_staff and (context.get('object', None) or context.get('model', None)):
        object_class = context.get('model', None)
        if not object_class:
            object_class = context['object'].__class__
        view_name = 'admin:%s_%s_add' % (object_class._meta.app_label,  object_class._meta.module_name)
        try:
            return make_link(reverse(view_name),
                _(u'Add {0}'.format(object_class._meta.verbose_name)), 'fugue/table.png',
                classes=['icon', 'alert_on_click'])
        except:
            pass

def django_admin_list_objects(request, context):
    if request and request.user.is_staff and (context.get('object', None) or context.get('model', None)):
        object_class = context.get('model', None)
        if not object_class:
            object_class = context['object'].__class__
        try:
            view_name = 'admin:%s_%s_changelist' % (object_class._meta.app_label,  object_class._meta.module_name)
            return make_link(reverse(view_name),
                _(u'List {0}'.format(object_class._meta.verbose_name)), 'fugue/table.png',
                classes=['icon', 'alert_on_click'])
        except:
            pass


def django_admin_navtree(request, context):
    if request and request.user.is_staff:
        coop_cms_navtrees = context.get('coop_cms_navtrees', None)
        if coop_cms_navtrees:
            tree_class = get_navtree_class()
            admin_tree_name = "{0}_{1}".format(tree_class._meta.app_label, tree_class._meta.module_name)
            if len(coop_cms_navtrees) == 1:
                tree = coop_cms_navtrees[0]
                url = reverse('admin:{0}_change'.format(admin_tree_name), args=[tree.id])
                label = _(u'Navigation tree')
            else:
                url = reverse('admin:{0}_changelist'.format(admin_tree_name))
                label = _(u'Navigation trees')
            return make_link(url, label, 'fugue/leaf-plant.png',
                classes=['icon', 'alert_on_click'])

def view_all_articles(request, context):
    if request and request.user.is_staff:
        return make_link(reverse('coop_cms_view_all_articles'), _(u'Articles'), 'fugue/documents-stack.png',
            classes=['icon', 'alert_on_click'])

@can_edit
def cms_media_library(request, context):
    if hide_media_library_menu():
        return
    
    if context.get('edit_mode'):
        return make_link(reverse('coop_cms_media_images'), _(u'Media library'), 'fugue/images-stack.png',
            'coopbar_medialibrary', ['icon', 'slide'])
        
@can_edit
def cms_upload_image(request, context):
    if hide_media_library_menu():
        return
    
    if context.get('edit_mode'):
        return make_link(reverse('coop_cms_upload_image'), _(u'Add image'), 'fugue/image--plus.png',
            classes=['coopbar_addfile', 'colorbox-form', 'icon'])

@can_edit
def cms_upload_doc(request, context):
    if hide_media_library_menu():
        return
    
    if context.get('edit_mode'):
        return make_link(reverse('coop_cms_upload_doc'), _(u'Add document'), 'fugue/document-import.png',
            classes=['coopbar_addfile', 'colorbox-form', 'icon'])

@can_add_article
def cms_new_article(request, context):
    if not context.get('edit_mode'):
        url = reverse('coop_cms_new_article')
        return make_link(url, _(u'Add article'), 'fugue/document--plus.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])

@can_add_link
def cms_new_link(request, context):
    if not context.get('edit_mode'):
        url = reverse('coop_cms_new_link')
        return make_link(url, _(u'Add link'), 'fugue/document--plus.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])

@can_add_article
def cms_set_homepage(request, context):
    if cms_no_homepage():
        return

    article = context.get('article', None)
    if context.get('edit_mode') and article and (not getattr(article, 'is_homepage', False)):
        url = reverse('coop_cms_set_homepage', args=[article.id])
        return make_link(url, _(u'Set homepage'), 'fugue/home--pencil.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])

@can_edit_article    
def cms_article_settings(request, context):
    #if context.get('edit_mode'):
    article = context['article']
    url = reverse('coop_cms_article_settings', args=[article.id])
    return make_link(url, _(u'Article settings'), 'fugue/gear.png',
        classes=['alert_on_click', 'colorbox-form', 'icon'])

@can_edit_object
def cms_save(request, context):
    if context.get('edit_mode'):
        #No link, will be managed by catching the js click event
        return make_link('', _(u'Save'), 'fugue/disk-black.png', id="coopbar_save",
            classes=['icon'])
    
def cms_save2(request, context):
    return
    if request and request.user.is_staff:
        url = context.get('coop_cms_edit_url', None)
        if url and context.get('edit_mode'):
            #No link, will be managed by catching the js click event
            return make_link('', _(u'Save'), 'fugue/disk-black.png', id="coopbar_save",
                classes=['icon'])

#@can_edit_article
#def cms_view(request, context):
#    if context.get('edit_mode'):
#        article = context['article']
#        return make_link(article.get_cancel_url(), _(u'View'), 'fugue/eye--arrow.png',
#            classes=['alert_on_click', 'icon', 'show-clean'])

@can_edit_object
def cms_cancel(request, context):
    if context.get('edit_mode'):
        url = context.get('coop_cms_cancel_url', None)
        if url:
            return make_link(url, _(u'Cancel'), 'fugue/cross.png', classes=['alert_on_click', 'icon'])
        
def cms_cancel2(request, context):
    return
    if request and request.user.is_staff:
        url = context.get('coop_cms_cancel_url', None)
        if url and context.get('edit_mode'):
            return make_link(url, _(u'Cancel'), 'fugue/cross.png',
                classes=['alert_on_click', 'icon'])
        
@can_edit_object
def cms_edit(request, context):
    if not context.get('edit_mode'):
        url = context.get('coop_cms_edit_url', None)
        if url:
            return make_link(url, _(u'Edit'), 'fugue/document--pencil.png', classes=['icon'])
        
def cms_edit2(request, context):
    return
    if request and request.user.is_staff:
        url = context.get('coop_cms_edit_url', None)
        if url and not context.get('edit_mode'):
            return make_link(url, _(u'Edit'), 'fugue/document--pencil.png', classes=['icon'])

@can_publish_article
def cms_publish(request, context):
    article = context.get('article')
    if article and ('draft' in context) :
        if context['draft']:
            
            return make_link(article.get_publish_url(), _(u'Draft'), 'fugue/lock.png',
                classes=['colorbox-form', 'icon'])
        else:
            return make_link(article.get_publish_url(), _(u'Published'), 'fugue/globe.png',
                classes=['colorbox-form', 'icon'])
        

def cms_extra_js(request, context):
    t = get_template("coop_cms/_coop_bar_js.html")
    return t.render(context)
    
def log_out(request, context):
    if request and request.user.is_authenticated() and request.user.is_staff:
        return make_link(reverse("django.contrib.auth.views.logout"), _(u'Log out'), 'fugue/control-power.png',
            classes=['alert_on_click', 'icon'])

@can_add_article
def cms_new_newsletter(request, context):
    if not context.get('edit_mode'):
        if getattr(settings, 'COOP_CMS_NEWSLETTER_TEMPLATES', None):
            url = reverse('coop_cms_new_newsletter')
            return make_link(url, _(u'Create newsletter'), 'fugue/document--plus.png',
                classes=['alert_on_click', 'colorbox-form', 'icon'])

@can_edit_newsletter
def edit_newsletter(request, context):
    if not context.get('edit_mode'):
        newsletter = context.get('newsletter')
        return make_link(newsletter.get_edit_url(), _(u'Edit'), 'fugue/document--pencil.png', classes=['icon'])

@can_edit_newsletter
def newsletter_admin(request, context):
    newsletter = context.get('newsletter')
    object_class = newsletter.__class__
    view_name = 'admin:%s_%s_change' % (object_class._meta.app_label,  object_class._meta.module_name)
    try:
        return make_link(reverse(view_name, args=[newsletter.id]),
            _(u'Admin {0}'.format(object_class._meta.verbose_name)), 'fugue/table.png',
            classes=['icon', 'alert_on_click'])
    except:
        pass

@can_edit_newsletter
def newsletter_articles(request, context):
    view_name = 'admin:coop_cms_newsletteritem_changelist'
    try:
        return make_link(reverse(view_name),
            _(u'Articles ordering'), 'fugue/table.png',
            classes=['icon', 'alert_on_click'])
    except:
        pass
    
@can_edit_newsletter
def cancel_edit_newsletter(request, context):
    if context.get('edit_mode'):
        newsletter = context.get('newsletter')
        return make_link(newsletter.get_absolute_url(), _(u'Cancel'), 'fugue/cross.png', classes=['icon'])

@can_edit_newsletter
def save_newsletter(request, context):
    newsletter = context.get('newsletter')
    post_url = context.get('post_url')
    if context.get('edit_mode') and post_url:
        return make_link(post_url, _(u'Save'), 'fugue/disk-black.png',
            classes=['icon', 'post-form'])

@can_edit_newsletter
def change_newsletter_settings(request, context):
    if not context.get('edit_mode'):
        newsletter = context.get('newsletter')
        url = reverse('coop_cms_newsletter_settings', kwargs={'newsletter_id': newsletter.id})
        return make_link(url, _(u'Newsletter settings'), 'fugue/gear.png',
            classes=['icon', 'colorbox-form', 'alert_on_click'])

#DEPRECATED
@can_edit_newsletter
def change_newsletter_template(request, context):
    if context.get('edit_mode'):
        newsletter = context.get('newsletter')
        url = reverse('coop_cms_change_newsletter_template', args=[newsletter.id])
        return make_link(url, _(u'Newsletter template'), 'fugue/application-blog.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])
###############

@can_edit_newsletter
def test_newsletter(request, context):
    newsletter = context.get('newsletter', None)
    if newsletter:
        url = reverse('coop_cms_test_newsletter', args=[newsletter.id])
        return make_link(url, _(u'Send test'), 'fugue/mail-at-sign.png',
            classes=['alert_on_click', 'colorbox-form', 'icon'])

#@can_edit_newsletter
#def schedule_newsletter(request, context):
#    if not context.get('edit_mode'):
#        newsletter = context.get('newsletter')
#        url = reverse('coop_cms_schedule_newsletter_sending', args=[newsletter.id])
#        return make_link(url, _(u'Schedule sending'), 'fugue/alarm-clock--arrow.png',
#            classes=['alert_on_click', 'colorbox-form', 'icon'])

def cms_add_fragment(request, context):
    if request:
        ct = ContentType.objects.get_for_model(Fragment)
        perm = '{0}.add_{1}'.format(ct.app_label, ct.model)
        if request.user.has_perm(perm):
            url = reverse("coop_cms_add_fragment")
            return make_link(url, _(u'Add fragment'), 'fugue/block--plus.png',
                    classes=['alert_on_click', 'colorbox-form', 'icon', 'if-fragments'])

def cms_edit_fragments(request, context):
    if request:
        ct = ContentType.objects.get_for_model(Fragment)
        perm = '{0}.change_{1}'.format(ct.app_label, ct.model)
        if request.user.has_perm(perm):
            url = reverse("coop_cms_edit_fragments")
            return make_link(url, _(u'Edit fragments'), 'fugue/block--pencil.png',
                    classes=['alert_on_click', 'colorbox-form', 'icon', 'if-fragments'])

def publication_css_classes(request, context):
    variable = context.get('article', None) or context.get('object', None)
    if variable:
        css_classes = []
        if hasattr(variable, 'is_draft') and callable(variable.is_draft) and variable.is_draft():
            return 'is-draft'
        elif hasattr(variable, 'is_archived') and callable(variable.is_archived) and variable.is_archived():
            return 'is-archived'    

def load_commands(coop_bar):
    
    coop_bar.register([
        [log_out],
        [django_admin, django_admin_edit_article, django_admin_edit_object, django_admin_navtree, view_all_articles],
        [cms_add_fragment, cms_edit_fragments],
        [cms_media_library, cms_upload_image, cms_upload_doc],
        [cms_new_newsletter, edit_newsletter, cancel_edit_newsletter, save_newsletter,
            change_newsletter_settings, newsletter_admin, newsletter_articles, 
            test_newsletter],
        [cms_edit, cms_save, cms_cancel, cms_edit2],
        [cms_new_article, cms_new_link, cms_article_settings, cms_set_homepage],
        [cms_publish],
    ])
    
    coop_bar.register_css_classes(publication_css_classes)
    
    coop_bar.register_header(cms_extra_js)
    
    #def js_code(request, context):
    #    return """<script>
    #    $(function() {
    #        $("a.modal").each(function(idx, elt) {
    #            $(elt).modal({
    #                remote: $(elt).attr('href')
    #            });
    #        });
    #    });
    #    </script>"""
    #
    #coop_bar.register_header(js_code)
