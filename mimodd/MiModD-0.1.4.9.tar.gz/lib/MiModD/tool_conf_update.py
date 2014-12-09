import os.path
import shutil
import imp
from xml.etree.ElementTree import ElementTree

# current problem:
# removal of sections is not working yet !!

def add_to_galaxy (galaxydir, force = False):
    """Register and install MiModD's tool wrappers for Galaxy.

    Adds a MiModD section to the Galaxy installation's tool_conf.xml file
    or updates the file.
    Copies the xml tool wrappers from the Python package to a new
    directory mimodd in the Galaxy installation's tools directory."""
    
    try:
        tool_conf_guess = os.path.join(galaxydir, 'tool_conf.xml')
    except:
        raise OSError('{0} does not seem to be a valid path'.format(galaxydir))

    this_package = 'MiModD'
    pkg_path = imp.find_module(this_package)[1]
    pkg_galaxy_data_path = os.path.join(pkg_path, 'galaxy_data')
    
    tool_conf_xml = ElementTree()
    outmost = tool_conf_xml.parse(tool_conf_guess)
                
    update_info = ElementTree().parse(os.path.join(pkg_galaxy_data_path, 'tool_conf_update.xml'))

    tools_to_link = {'NGS_QC' : ('fastq/fastq_paired_end_splitter.xml', 'fastq/fastq_paired_end_deinterlacer.xml')}

    for section in tool_conf_xml.iter("section"):
        if this_package == section.attrib['name']:
            if force:
                outmost.remove(section)
            else:
                raise RuntimeError("A MiModD section already exists in this Galaxy's tool_conf.xml. Use force to overwrite existing installation.")

    for search in tools_to_link:
        for section in tool_conf_xml.iter('section'):
            if section.attrib['id'] == search:
                found_section = section
                break
            else:
                found_section = None
        if found_section is not None:
            for tool in found_section.iter('tool'):
                if tool.attrib['file'] in tools_to_link[search]:
                    update_info.append(tool)

    outmost.append(update_info)
    tool_conf_xml.write(tool_conf_guess)

    # now force refresh of Galaxy Tools panel by removing MiModD from the integrated_tool_panel.xml
    integrated_tools_xml = ElementTree()
    outmost = integrated_tools_xml.parse(os.path.join(galaxydir, 'integrated_tool_panel.xml'))
    for section in integrated_tools_xml.iter('section'):
        if this_package == section.attrib['name']:
            outmost.remove(section)
    integrated_tools_xml.write(os.path.join(galaxydir, 'integrated_tool_panel.xml'))

    print ('Successfully changed the tool configuration file at {0}.'.format(tool_conf_guess))

    galaxy_wrappers_target_dir = os.path.join(galaxydir, 'tools/mimodd')
    
    try:
        shutil.copytree(os.path.join(pkg_galaxy_data_path, 'mimodd'), galaxy_wrappers_target_dir)
    except:
        if force:
            print ('Trying to remove old MiModD wrappers directory ...')
            shutil.rmtree(galaxy_wrappers_target_dir)
            shutil.copytree(os.path.join(pkg_galaxy_data_path, 'mimodd'), galaxy_wrappers_target_dir)
        else:
            raise
        
    print ('Successfully copied Galaxy tool wrappers to {0}.'.format(galaxy_wrappers_target_dir))
