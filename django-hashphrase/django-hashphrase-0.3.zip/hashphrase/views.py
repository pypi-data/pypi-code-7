from django.template import RequestContext
from django.http import HttpResponseNotFound, HttpResponse

def hash_link(request, key):
    """
    all hash links go to this function.

    """
    from models import HashLink
    if key:
        return_dict = {}
        HashLink.verify_and_call_action_function(request,key, return_dict) #may call your registered function or the global default_action function
        verified = return_dict['verified']
        if 'return_obj' in return_dict:
            return return_dict['return_obj'] #registered function should return render_to_response or HttpResponse
        elif 'action' not in return_dict:
            return HttpResponse('Invalid action.') #maybe verified or not, check ['verified'] but no registered function
        else:
            return HttpResponse('Not verified.')
    return HttpResponse('Invalid link.')


def default_action_on_error(request, has_error, error_code, hash_link, content_obj):
    return HttpResponseNotFound("Permission denied.")



def test_success(request, has_error, error_code, hash_link, content_obj):
    """
    use hashphrase_register decorator to register this function to be called when
    users click on the email link.
    be sure to check has_error. If not verified, has_error = True
    See HashLink class for error code definition
    """
    if has_error or not hash_link or not content_obj:
        from hashphrase.models import HashLink
        ret = "Invalid email link."
        if error_code == HashLink.ERR_EXPIRED:
            ret = "Link expired."
        elif error_code == HashLink.ERR_INVALID_USER:
            ret = "Needs to login."
        elif error_code == HashLink.ERR_INVALID_LINK:
            ret = "Invalid link."
        return HttpResponse(ret)
    return HttpResponse("Successful.")



def hash_link_test(request):
    from django.conf import settings
    if not hasattr(settings, 'DEBUG') or not settings.DEBUG:
        return HttpResponseNotFound()
    from models import HashLink
    from django.contrib.auth.models import User
    user = User.objects.get(id=1)

    from . import hashphrase_functions

    cur_datetime = hashphrase_functions.current_datetime_function()
    action = 'default_action2'
    hash_phrase = HashLink.gen_key(request.user, user, cur_datetime, action=action)

    from django.template import Template
    template = Template("""{{ verified }}<a href="/hl/{{ hash_phrase }}">test hash link {{ hash_phrase }}</a>""")
    c = RequestContext(request, {'hash_phrase': hash_phrase,'verified':''})
    rendered = template.render(c)
    return HttpResponse(rendered)
