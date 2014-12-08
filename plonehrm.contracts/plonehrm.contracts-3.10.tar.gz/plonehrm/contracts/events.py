import logging

from Products.plonehrm.utils import apply_template_of_tool

logger = logging.getLogger('plonehrm.contracts.events')


def apply_template(object, event, rename=True):
    """After initializing a contract, set text and title based on template.

    If rename is True (the default) we will rename the object after
    setting its title.  Within tests this may fail, so there it can
    help to set it to False.  Yes, this is a hack.
    """
    template_page = apply_template_of_tool(object, 'portal_contracts')

    # Set the title to the title of the template (appending 1, 2,
    # 3...), if it has not been set explicitly.
    if object.Title():
        return
    employee = object.get_employee()
    title = template_page.Title()
    if employee is not None:
        numbers = [0]
        for contract in employee.getFolderContents(
                dict(portal_type=object.portal_type)):
            if not contract.Title.startswith(title):
                continue
            number = contract.Title.split(' ')[-1]
            try:
                numbers.append(int(number))
            except ValueError:
                continue
        title += ' %d' % (max(numbers) + 1)
    object.title = title
    # Now we have a title, we rename the object to something nicer
    # than 'contract.2009-05-15.1869364249'.
    if not rename:
        return
    object._renameAfterCreation()
