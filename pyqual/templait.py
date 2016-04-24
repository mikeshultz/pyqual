""" An ultra simple templating system """

import re

__author__ = "Mike Shultz"
__copyright__ = "Copyright 2016, Mike Shultz"
__credits__ = ["Mike Shultz"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Mike Shultz"
__email__ = "mike@mikeshultz.com"
__status__ = "Production"

class TemplateError(Exception): pass
class TemplateEmpty(TemplateError): pass
class TemplateNotFound(TemplateError): pass

class Templait:
    """ A template class for rendering template files.

        To use, initialize Templait() with the filename of the template and a 
        dictionary of replacement tags. To return rendered string, call render()

        template.txt:
            My name is {{ name }} and I like templates.
        example.py:
            t = Templait('template.txt', { 'name': 'Joe Bob', })
            print t.render()

        Output:
            "My name is Joe Bob and I like templates."
    """
    def __init__(self, fl, diction = None):
        #self.file = file
        self.diction = diction

        self._templateString = ''
        self._fh = None

        if not fl:
            raise TemplateError('Template not provided.')
        self.filename = fl
        self._set_file(fl)

    def __str__(self):
        return self.render()
    def __utf8__(self):
        return self.__str__()

    def _set_file(self, fl):
        """ Get the template file """
        try:
            self._fh = open(fl or self.file, 'r')
        except IOError as e:
            raise TemplateNotFound(e)
        self._templateString = self._fh.read()
        return True
    def _get_file(self):
        return self._templateString
    file = property(_get_file, _set_file)

    def _handle_tags(self, diction = None):
        """ Replace template tags with supplied vars """
        st = '\\{\\{[ ]*'
        en = '[ ]*\\}\\}'

        if not self._templateString:
            raise TemplateError('No template to process.')
        d = diction or self.diction
        if d:
            for k, v in d.items():
                pat = st + k + en
                self._templateString = re.sub(pat, v, self._templateString)
        self._templateString = re.sub(st + '[\w\d\s]+' + en, '', self._templateString)
        return self._templateString

    def render(self):
        """ Render the template and return it as a string """
        self.file = self.filename
        return self._handle_tags()
