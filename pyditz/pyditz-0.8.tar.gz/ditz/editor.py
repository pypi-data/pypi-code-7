"""
Text editor.

TODO: wire up validity loop.  But what happens if it's invalid?  Loop
outside edit, ask whether they want to re-edit or abort.
"""

import os
import yaml
import tempfile


class TextEditor(object):
    prefix = 'tmp-'
    suffix = '.txt'
    textmode = True
    filetag = "<input>"

    def __init__(self, program, text=''):
        #: The editor program.
        self.program = program

        #: Original text.
        self.original = text

        #: The text after editing.
        self.text = text

        #: Validation error message from last edit, or None.
        self.error = None

    def edit(self):
        "Edit the text, and return subprocess status."

        # Write text to a temp file.
        fp, filename = tempfile.mkstemp(prefix=self.prefix,
                                        suffix=self.suffix,
                                        text=self.textmode)
        os.write(fp, self.text)
        os.close(fp)

        try:
            # Run the editor.
            command = '%s "%s"' % (self.program, filename)
            status = os.system(command)

            # Get the edited text.
            with open(filename) as fp:
                self.text = fp.read()

            # Check for validity.
            self.error = None
            with open(filename) as fp:
                msg = self.validate(fp)
                if msg:
                    self.error = msg.replace(filename, self.filetag)

        finally:
            # Clean up.
            os.remove(filename)

        return status

    @property
    def modified(self):
        "Whether text has been modified."
        return self.text != self.original

    def validate(self, fp):
        "Return validation error text or None."
        return None


class YAMLEditor(TextEditor):
    suffix = '.yaml'

    def validate(self, fp):
        try:
            yaml.safe_load(fp)
        except yaml.error.YAMLError as err:
            return str(err)

        return None


if __name__ == "__main__":
    path = "../bugs/project.yaml"
    from ditz.objects import DitzObject

    editor = YAMLEditor("pluma", text=open(path).read())
    print editor.edit()

    print "Modified:", editor.modified
    print "Error:", editor.error
