"""
    This file is part of the cream web paste libs.
    See ../paster.py for license details.
"""

from cream.util import cached_property

from basic_service import *

class DPaste(PasteService):
    __name__ = "DPaste"
    fields = ('content', 'language', 'name', 'title', 'hold')
    host = 'http://dpaste.com'

    @cached_property
    def languages(self):
        languages_regexp = "<option value=\"(.+)\">(.+)</option>"
        content = '\n'.join([line for line in \
            urllib.urlopen(self.host).read().split("\n") \
            if line.startswith("    <o")])
        try:
            language_list = re.findall(languages_regexp, content)
        except IndexError:
            raise NoLanguagesFound(name=self.__name__)
        d = dict(language_list)
        d['Plain'] = d['" selected="selected']
        del d['" selected="selected']
        return d

    @property
    def default_language(self):
        return ''


    def do_paste(self, code, language=None, hold=False, name='', title=''):
        url = 'http://dpaste.com/api/v1/'

        params = {
            'language' : language,
            'content' : code,
            'name' : name,
            'hold' : ('on', '')[hold],
            'title' : title,
        }

        request = urllib.urlopen(url, urllib.urlencode(params))

        if request.getcode() != 200:
            return 'Error'
        else:
            return request.geturl()

