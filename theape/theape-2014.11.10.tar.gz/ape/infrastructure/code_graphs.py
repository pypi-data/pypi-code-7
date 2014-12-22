
# python standard library
import shlex
import subprocess


def module_diagram(module, project, output_format='png'):
    """
    Creates a dependency diagram for the module given.

    :param:

     - `module`: path to the module
     - `project`: name to use to distinguish the output file
     - `output_format`: format for graph-image file

    :return: name of image file
    """
    command = 'pyreverse -o {0} -ASmy -k -p {1} {2}'.format(output_format,
                                                   project,
                                                   module)
    try:                                               
        subprocess.call(shlex.split(command))
    except OSError as error:
        print error
        print "Is pylint installed?"
    return "classes_{0}.{1}".format(project, output_format)    


def class_diagram(class_name, module, output_format='png',
                  add_module='n', level=1, filter="ALL"):
    """
    Creates a more-detailed class diagram for a single class

    :param:

     - `class_name`: the name of the class to graph
     - `module`: path to the file with the class
     - `output_format`: graphviz output format
     - `add_module`: if 'y', add module name to class (e.g. module.class)
     - `level`: depth to pursue ancestors and associated classes
     - `filter`: What to include (the `filter` option)

    :return: name of image file created
    """
    command = 'pyreverse -c {c} -m{m} -a{l} -s{l} -f {f} -o {o} {n}'.format(c=class_name,
                                                                            m=add_module,
                                                                            l=level,
                                                                            f=filter,
                                                                            o=output_format,
                                                                            n=module)

    subprocess.call(shlex.split(command))    
    return "{0}.{1}".format(class_name, output_format)
