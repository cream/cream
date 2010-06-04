"""
    This file is part of the cream web paste libs.
    See ../paster.py for license details.
"""

from basic_service import *

class RAFBPaste(PasteService):
    __name__ = "RAFB paste"
    host = 'http://rafb.net/paste'
    new_paste_url = '%s/index.html' % host
    paste_url = '%s/paste.php' % host
    fields = ('lang', 'text', 'nick', 'desc')

    @property
    def languages(self):
        languages_regexp = "<option value=\"(.+)\">(.+)</option>"
        content = '\n'.join([line for line in \
            urllib.urlopen(self.new_paste_url).read().split("\n") \
            if line.startswith("    <o") and not "selected" in line])
        try:
            language_list = re.findall(languages_regexp, content)
            language_list.append(('C++', 'C++'))
        except IndexError:
            raise NoLanguagesFound(name=self.__name__)
        return dict(language_list)

    @property
    def default_language(self):
        return 'C++'

    def do_paste(self, code, language=None, nickname='', description=''):
        url_regexp = "URL: (http://rafb.net/p/[a-zA-Z0-9]+.html)"
        if language:
            try:
                language = self.languages[language]
            except KeyError:
                raise LanguageNotFound(language=language)
        params = {
            'lang' : language or self.default_language,
            'text' : code,
            'nick' : nickname,
            'desc' : description,
        }
        request = urllib.urlopen(self.paste_url, urllib.urlencode(params))
        return re.findall(url_regexp, request.read())[0]