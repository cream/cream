"""
    This file is part of the cream web paste libs.
    See ../paster.py for license details.
"""

from basic_service import *
from lodgeitlib import lodgeit

class PocooPaste(PasteService):
    __name__ = "Pocoo paste"
    @property
    def languages(self):
        return lodgeit.languages

    @property
    def default_language(self):
        return 'text'

    def do_paste(self, code, language=None):
        if language is None:
            language = self.default_language
        return lodgeit.get_paste_by_id(
            lodgeit.new_paste(unicode(code), language)
        ).url
