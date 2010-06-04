"""
    This file is part of the cream web paste libs.
    See ../paster.py for license details.
"""

from basic_service import *

class DPaste(PasteService):
    __name__ = "DPaste"
    fields = ('content', 'language', 'name', 'title', 'hold')
    host = 'http://dpaste.com'

    @property
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
        d['--removeme--'] = d['" selected="selected']
        del d['" selected="selected']
        return d

    @property
    def default_language(self):
        return ''

    def do_paste(self, code, language=None, hold=False, name='', title=''):
        url_regexp = "URL: (%s/hold/[0-9]+)" % self.host
        if language:
            try:
                language = self.languages[language]
            except KeyError:
                raise LanguageNotFound(language=language)
        params = {
            'language' : language or self.default_language,
            'content' : code,
            'name' : name,
            'hold' : ('on', '')[hold],
            'title' : title,
        }
        request = urllib.urlopen(self.host, urllib.urlencode(params))
        return re.findall(url_regexp, request.read())[0].replace('/hold', '')