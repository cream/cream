"""
    This file is part of the cream web paste libs.
    See ../paster.py for license details.
    WON'T WORK because of tokens
"""

from basic_service import *

class InyokaPaste(PasteService):
    __name__ = "InyokaPaste"
    fields = ('language', 'title', 'code')
    host = 'http://paste.ubuntuusers.de'

    @property
    def languages(self):
        languages_regexp = "<option value=\"(.+)\">(.+)</option>"
        content = urllib.urlopen(self.host).read()
        try:
            language_list = re.findall(languages_regexp, content)
        except IndexError:
            raise NoLanguagesFound(name=self.__name__)
        return dict(language_list)

    @property
    def default_language(self):
        return 'text'

    def do_paste(self, code, language=None, title=''):
        token_regexp = "name=\"_form_token\" value=\"([a-z0-9]{32})\""
        url_regexp = "URL: (%s/[0-9]+)" % self.host
        token = re.findall(token_regexp, urllib.urlopen(self.host).read())[0]
        if language:
            try:
                language = self.languages[language]
            except KeyError:
                raise LanguageNotFound(language=language)
        params = {
            'language' : language or self.default_language,
            'code' : code,
            'title' : title,
            '_form_token' : token,
        }
        request = urllib.urlopen(self.host, urllib.urlencode(params))
        return request.read()
        return re.findall(url_regexp, request.read())[0]