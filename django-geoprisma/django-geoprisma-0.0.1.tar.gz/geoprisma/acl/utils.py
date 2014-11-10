# -*- coding: utf-8 -*-
from .models import Action, Right
from geoprisma.models import Resource
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def isAuthorized(user, ress_name, action_name):
    """
    Valid if a user has the right to do an action on a ressource.

    """
    try:
        if user.is_superuser:
            return True
    
        #On recupere les usergroups de l'utilisateur
        usergroups = Group.objects.filter(user__id__exact=user.pk)
    
        #On recupere la ou les resource(s)
        ress = Resource.objects.filter(Q(acl_name=ress_name) | Q(name=ress_name))
    
        #On recupere l'action
        action = Action.objects.get(name__iexact=action_name)
    
        # On traite chaques resources obtenues
        for res in ress:
            #On recupere les id des usergroups des droits concernant la ressource et l'action passés en parametre
            rights_usergroup = Right.objects.filter(id_resource=res, actions__id__exact=action.pk).values_list('id_group', flat=True)
    
            #On regarde si un des usergroups de l'utilisateur est dans les 'rights_usergroup'
            for usergroup in usergroups:
                if usergroup.pk in rights_usergroup:
                    return True
        return False
    
    except ObjectDoesNotExist:
        return False
