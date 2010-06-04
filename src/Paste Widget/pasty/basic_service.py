import urllib
import re

class GeneralError:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __repr__(self):
        return "%s args=%s and kwargs=%s" % (self.name, self.args, self.kwargs)

class NoLanguagesFound(GeneralError):
    name = "NoLanguagesFound"

class LanguageNotFound(GeneralError):
    name = "LanguageNotFound"

class PasteService(object):
    def __init__(self):
        """
            Inits the PasteService.
        """
        pass

    @property
    def languages(self):
        """
            Get the languages the pastebin supports (syntax hightlighting)
            @returns: a dict containing the languages
        """
        pass

    @property
    def default_language(self):
        """
            Get the pastebin's default syntax hightlighting language
            (`text` in most cases)
            @returns: the pastebin's default language as string
        """
        pass

    def do_paste(self, code, language=None):
        """
            Execute the paste.
            @param code: The code to paste
            @param language: The language to highlight
            @returns: The url of the paste
        """
        pass