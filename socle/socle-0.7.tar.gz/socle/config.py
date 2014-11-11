
import importlib
import os
import re
import facts
import menu
import sys
import logging
from datetime import datetime
from menu import choice, CanceledException

def mainloop():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Starting SoC configuration utility")

    now = datetime.now()
    if now.year < 2015:
        logging.critical("The clock of the machine seems wrong, hardware is reporting: %s", now)

    PLUGINS_PATH = os.path.join(os.path.dirname(__file__), "plugins")
    BOARDS_PATH = os.path.join(os.path.dirname(__file__), "boards")

    sys.path.append(PLUGINS_PATH)
    sys.path.append(BOARDS_PATH)

    # Load plugins for configuring timezones, locales, network interfaces etc
    plugins = []
    for filename in os.listdir(PLUGINS_PATH):
        if not filename.startswith("_") and filename.endswith(".py"):
            modname = "socle.plugins.%s" % filename[:-3]
            plugins.append(importlib.import_module(modname))

    # Detect board and populate main menu with platform specific options
    def detect_board():
        for filename in os.listdir(BOARDS_PATH):
            if not filename.startswith("_") and filename.endswith(".py"):
                mod = importlib.import_module("socle.boards.%s" % filename[:-3])
                for obj in dir(mod):
                    cls = getattr(mod, obj)
                    if hasattr(cls, "match"):
                        if cls.match(facts):
                            logging.info("Probed board %s", cls.NAME)
                            return cls.instantiate()
                        else:
                            logging.debug("Failed to match %s", cls.NAME)
        from boards.generic import GenericBoard
        logging.info("Falling back to generic board")
        return GenericBoard()

    board = detect_board()

    MAINMENU = (
#        ("Enable OpenSSH",            NotImplemented),
#        ("Disable boot to desktop",   NotImplemented),
    )

    for plugin in plugins:
        MAINMENU += plugin.MENU_ENTRIES

    MAINMENU = tuple(sorted(MAINMENU, key=lambda (k,v):k))

    def do_shell():
        menu.screen.finish()
        menu.screen = None
        os.system("bash")

    def do_reboot():
        os.system("reboot")
        exit(0)


    def do_halt():
        os.system("shutdown -h now")
        exit(0)

    MAINMENU = (
        ("Drop to shell", do_shell),
    ) + tuple(sorted(MAINMENU + board.mainmenu())) + (
        ("Reboot", do_reboot),
        ("Shut down", do_halt)
    )
    
    while True:
        try:
            submenu = choice(
                MAINMENU,
                "SoC configuration utility",
                "Detected board: " + board.NAME + "\n" + 
                "Running: " + facts.LSB_DISTRIBUTION + " " + facts.LSB_RELEASE + " (" + facts.LSB_CODENAME + ")",
                action_cancel="Exit"
            )
        except CanceledException:
            break

        try:
            submenu()
        except CanceledException:
            pass


if __name__ == "__main__":
    mainloop()
