
class NoScreen():
    def finish(self):
        pass

screen = None

try:
    import snack
except ImportError:
    try:
        import newt as snack
    except ImportError:
        print "Could not import newt, are you sure either python-snack or python-newt package is installed?"
        snack = None
    else:
        print "Could not import snack, falling back to newt..."


import sys
from facts import TTY

class CanceledException():
    pass

    
def prepare():
    """
    Unobtrusively load snack if we're not connected via UART
    """
    global screen
    if not screen:
        if snack and not TTY.startswith("/dev/ttyS"):
                import atexit
                screen=snack.SnackScreen()
                atexit.register(screen.finish)
                oldexcepthook = sys.excepthook
                def newexcepthook(*args):
                    screen.finish()
                    oldexcepthook(*args)
                sys.excepthook = newexcepthook
        else:
                screen = NoScreen()
		
def choice(choices, title="Select", help="Select one of following", action_ok="OK", action_cancel="Cancel"):
    global screen
    prepare()
    choices = tuple(choices)
    MAX_HEIGHT = 10
    if not isinstance(screen, NoScreen):
        action, selected = snack.ListboxChoiceWindow(screen,
            title,
            help,
            choices,
    		buttons=((action_ok, ""), (action_cancel, "cancel")),
    		height=MAX_HEIGHT if len(choices) > MAX_HEIGHT else -1,
    		scroll=len(choices) > MAX_HEIGHT)
        if action == "cancel":
            raise CanceledException()
        return selected
    else:
        print
        print title
        print "=" * len(title)
        print help
        print
        for index, (title, value) in enumerate(choices):
            print "%d. %s" % (index+1, title)
        print "q. Cancel"
        print
        while True:
            try:
                sys.stdout.write("> ")
                line = sys.stdin.readline()
                if line == "q\n" or not line:
                    raise CanceledException()
                return choices[int(line) - 1][1]
            except IndexError, ValueError:
                print "Invalid selection, try again"

def form(fields, title="Fill fields", help="Fill following fields", action_ok="OK", action_cancel="Cancel"):
    global screen
    prepare()
    if not isinstance(screen, NoScreen):
        action, selection = snack.EntryWindow(screen,
            title,
            help,
            fields,
            buttons=((action_ok, ""), (action_cancel, "cancel")))
        if action == "cancel":
            raise CanceledException()
        return selection
    else:
        raise NotImplementedError

