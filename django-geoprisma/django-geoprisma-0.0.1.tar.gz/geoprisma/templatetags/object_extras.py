from django import template
register = template.Library()

def callMethod(obj, methodName):
    method = getattr(obj, methodName)
 
    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()
 
def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
     
    obj.__callArg += [arg]
    return obj
 
register.filter("call", callMethod)
register.filter("args", args)

def check_type(obj, stype):
    try:
        t = obj.__class__.__name__
        return t.lower() == str(stype).lower()
    except:
        pass
    return False
register.filter('obj_type', check_type)