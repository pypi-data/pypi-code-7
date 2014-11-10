from django import template
from geoprisma.models import Service
register = template.Library()


@register.simple_tag
def printWidgetOptionss(options):
    """
    Construit un tableau de clef:valeur pour l'affichage javascript
    
    Args:
        options: Liste d'option
    Returns:
        La liste formatee
    """
    options = regroupOptionsByName(options)
    i = 1
    strOptions = '{\n'
    for option in options:
        if type(option) is list:
            j = 1
            strOptions += '"'+option[0].name+'s": ['
            for suboption in option:
                strOptions += printOptionByType(suboption.value)
                if j < len(option):
                    strOptions += ','
                    j += 1
                else:
                    strOptions += ']'
            if i < len(options):
                strOptions += ',\n'
                i += 1
        else:
            strOptions += '"' + option.name + '":' + printOptionByType(option.value)
            if i < len(options):
                strOptions +=',\n'
                i += 1
    strOptions += '}'
    return strOptions

def regroupOptionsByName(options):
    """
    Regroupe les option d'une liste par nom
    
    Args:
        options: La liste d'option
    Returns:
        Liste d'option groupe
    """
    groupedOptions = []
    groups = {}
    for option in options:
        groups.setdefault(option.name, list()).append(option)
    for key in groups:
        if len(groups[key]) > 1:
            groupedOptions.append(groups[key])
        else:
            groupedOptions.append(groups[key].pop())
    return groupedOptions
        
def printOptionByType(option):
    """
    Format l'option selon son type
    
    Args:
        option: L'option
    Returns:
        L'option formatee
    """
    if option.isdigit() or option == "true" or option == "false":
        return option
    else:
        return '"'+ option.replace("\"","'") +'"'
    


