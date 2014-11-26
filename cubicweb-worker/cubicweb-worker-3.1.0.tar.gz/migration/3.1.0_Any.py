add_cube('subprocess')

add_attribute('CWWorkerTask', 'use_subprocess')
add_relation_definition('Subprocess', 'handle_workertask', 'CWWorkerTask')
