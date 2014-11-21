from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


def _correct_import(name):
    m = __import__(name)
    for n in name.split(".")[1:]:
        m = getattr(m, n)
    return m

def _import_from_string(long_name, file_only=False):
    try:
        last_dot = long_name.rfind('.')
        module_name = long_name[:last_dot]
        function_name = long_name[last_dot+1:]
        module = _correct_import(module_name)
        if not file_only:
            func = vars(module)[function_name]
        else:
            func = None
    except Exception, ex:
        func = None
    return func


class HashLink(models.Model):
    """
    To facilitate sending a URL in emails that users can click on
    """
    ALLOWED_MODELS = models.Q(model='Alert') | models.Q(model='Appointment')
    content_type = models.ForeignKey(ContentType, limit_choices_to=ALLOWED_MODELS) #here the real type of content object is stored
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(User, related_name='hashphrase_user')
    expiration_datetime = models.DateTimeField(null=True,blank=True)
    creation_datetime = models.DateTimeField()
    allow_anonymous = models.BooleanField(default=False)
    KEY_LENGTH = 16
    key = models.CharField(max_length=KEY_LENGTH, db_index=True)
    #what to call after verification, leave blank for not calling anything
    action = models.CharField(max_length=128, blank=True, default='')

    ERR_INVALID_USER = 100 #allow anonymous will by pass this check
    ERR_EXPIRED = 200 #not setting expiration date will bypass this check
    ERR_INVALID_LINK = 300

    @classmethod
    def gen_key(cls, user, other_object, cur_datetime, allow_anonymous=False, expiration_datetime=None, action=''):
        import string, random

        #reduce duplicate
        existing = HashLink.objects.filter(user=user, object_id=other_object.id, content_type__model=other_object.__class__.__name__, allow_anonymous=allow_anonymous, action=action)
        if existing.count():
            r = existing[0]
            random_str = r.key
        else:
            max_loop = 3
            random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(cls.KEY_LENGTH))
            while True:
                #make sure no conflict
                if not HashLink.objects.filter(key=random_str).exists():
                    break

                random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(cls.KEY_LENGTH))
                max_loop -= 1
                if max_loop < 0:
                    break #Todo: log it.

            r = HashLink(content_object=other_object, user=user, creation_datetime=cur_datetime,key=random_str,
                allow_anonymous=allow_anonymous, expiration_datetime=expiration_datetime, action=action)
            r.save()
        import base64
        encoded_category_name = base64.urlsafe_b64encode(str(action))
        return "%s%s" %(random_str, encoded_category_name)

    @classmethod
    def verify_and_return_object(cls, user, raw_key, return_dict):
        random_str = raw_key[:cls.KEY_LENGTH]
        encoded_action = raw_key[cls.KEY_LENGTH:]
        import base64
        try:
            decoded_action =  base64.urlsafe_b64decode(str(encoded_action))
        except:
            decoded_action = 'default_action'

        return_dict['action'] = decoded_action
        return_dict['verified'] = False
        return_dict['error_code'] = cls.ERR_INVALID_LINK

        obj = HashLink.objects.filter(key=random_str)
        if obj:
            obj = obj[0]

            return_dict['hashphrase_obj'] = obj
            return_dict['content_obj'] = obj.content_object
            return_dict['action'] = obj.action #replace with stored action if verified

            if not obj.allow_anonymous:
                if user != obj.user:
                    return_dict['verified'] = False
                    return_dict['error_code'] = cls.ERR_INVALID_USER
                    return False
            if obj.expiration_datetime:
                from gradsite.helpers import current_datetime
                cur_datetime = current_datetime()
                if cur_datetime > obj.expiration_datetime:
                    return_dict['verified'] = False
                    return_dict['error_code'] = cls.ERR_EXPIRED
                    return False

            return_dict['verified'] = True
            return_dict['error_msg'] = ''

            return True

        return False



    @classmethod
    def verify_and_call_action_function(cls, request, raw_key, return_dict):

        cls.verify_and_return_object(request.user, raw_key, return_dict)

        hashphrase_obj = return_dict.get('hashphrase_obj',None)
        content_obj = return_dict.get('content_obj', None)
        suggested_action = return_dict.get('action', None)
        has_error = not return_dict.get('verified', False)

        if not suggested_action:
            return

        from helpers import hashphrase_functions
        from django.conf import settings


        action_module, action_function = hashphrase_functions.get_module_and_function('default_action') #global default
        if suggested_action in hashphrase_functions.get_category_names():
            action_module, action_function = hashphrase_functions.get_module_and_function(suggested_action)

        try:
            module = _correct_import(action_module)
        except Exception, ex:
            has_error = True
            if settings.DEBUG:
                print "Unable to find action_module: %s" %(action_module,)
                print ex
        try:
            func = vars(module)[action_function]
        except Exception, ex:
            has_error = True
            if settings.DEBUG:
                print "Unable to find action_function: %s" %(action_function,)
                print ex
        try:
            return_obj = func(request, has_error, return_dict.get('error_code', ''), hashphrase_obj, content_obj)
            return_dict['return_obj'] = return_obj
        except Exception, ex:
            has_error = True
            if settings.DEBUG:
                print ex

        return


def generate_hashphrase(user, other_object, cur_datetime, allow_anonymous=False, expiration_datetime=None, action=''):
    return HashLink.gen_key(user, other_object, cur_datetime, allow_anonymous=allow_anonymous,
        expiration_datetime=expiration_datetime, action=action)