# -*- coding: utf-8 -*-
# Copyright (c) 2008 Sebastian Wiesner <basti.wiesner@gmx.net>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
    lodgeitlib
    ==========

    A convenient client library to the pocoo pastebin at
    http://paste.pocoo.org.


    :var LODGEIT_ADDRESS: The address of the Lodgeit website
    :var SERVICE_ADDRESS: The address of the Lodgeit XML RPC service
    :var lodgeit: A default lodgeit instance poiting to
                  http://paste.pocoo.org


    :author: Sebastian Wiesner
    :contact: basti.wiesner@gmx.net
    :copyright: 2008 by Sebastian Wiesner
    :version: 0.1
    :license: MIT
"""


__version__ = '0.1'


from xmlrpclib import ServerProxy
from datetime import datetime
from urlparse import urljoin


LODGEIT_ADDRESS = 'http://paste.pocoo.org'
SERVICE_ADDRESS = urljoin(LODGEIT_ADDRESS, 'xmlrpc/')


class UnsupportedLanguageError(Exception):
    """Inidicates an unsupported language"""


class Paste(object):
    """
    Wraps a single paste.

    :ivar lodgeit: The `Lodgeit` instance, which fetched this paste
    :ivar id: The unique paste id
    :ivar code: The paste code
    :ivar parsed_code: TODO: what is this one?
    :ivar datetime: The date of publication
    :ivar language: The language of the paste
    :ivar parent_id: The id of the parent paste
    :ivar relative_url: The relative url of the paste
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_parent(self):
        """Returns the parent paste.

        :returntype: `Paste`"""
        return self.lodgeit.get_paste_by_id(self.parent_id)

    def __repr__(self):
        return '<Paste(%i) at %s>' % (self.id, id(self))

    def __str__(self):
        return self.code

    @property
    def url(self):
        """The complete url of this paste."""
        return (urljoin(self.lodgeit.address, self.relative_url)
                if self.relative_url else None)

    @property
    def language_desc(self):
        """The language description."""
        return (self.lodgeit.languages[self.language]
                if self.language else None)


class Lodgeit(object):
    """
    Wraps the Lodgeit XML RPC service in a convenient interface.

    Caching
    -------

    This class performs internal caching, if the instance attribute
    `caching` is ``True``. If caching is enabled, pastes, which are fetched
    by id, are first looked up in an internal cache.

    *Note*: Method, which fetch pastes based on their time cannot be
    cached. These will always cause network traffic. This affects the
    `get_last_paste` and 'get_recent_pastes` methods.

    Language caching
    ~~~~~~~~~~~~~~~~

    The list of available languages is fetched, when it's first needed. It
    is always cached, any further language access will point to an internal
    list and not cause any network traffic. If you have long-running
    processes (long running means more than some days here!), you can use
    `reset_languages` to erase the internal list of languages.

    You can use the 'has_languages' property to query the state of the
    language cache.

    Thread safety
    -------------

    This class is not thread-safe, at least if caching is enabled. Multiple
    threads should not access this pastebin without proper synchronisation.

    :ivar address: The address of the lodgeit web interface
    :ivar service_address: The address of the xmlrpc service, this instance
      is connected to. *Note*: Changing this attribute does not affect the
      connection, it will still use the old value.
    :ivar caching: Whether method class are cached or not
    """

    def __init__(self, caching=True, address=LODGEIT_ADDRESS,
                 service_address=SERVICE_ADDRESS):
        """Creates a new lodgeit instance.

        :param caching: If ``True``, `Paste` instances are cached to avoid
                        network traffic.
        :param address: The address of the lodgeit web interface
        :param service_address: The address of the lodgeit xml rpc interface
        """
        self.address = address
        self.service_address = service_address
        self._lodgeit = ServerProxy(service_address, allow_none=True)
        self._cache = {}
        self._languages = None
        self.caching = caching

    def __repr__(self):
        return '<Lodgeit(%r) at %s>' % (self.service_address, id(self))

    def _get_paste_from_result(self, result):
        """Converts a paste dictionary as returned by the service into a
        `Paste` object and puts the object into the cache.
        """
        if not result:
            return None
        paste = Paste(lodgeit=self,
                      id=result['paste_id'],
                      parent_id=result['parent_id'],
                      code=unicode(result['code']),
                      parsed_code=result['parsed_code'],
                      language=result['language'],
                      datetime=datetime.fromtimestamp(result['pub_date']),
                      relative_url=result['url'],)
        self._cache[paste.id] = paste
        return paste

    def get_paste_by_id(self, id):
        """Returns the paste with 'id`. This method is cached, if `caching`
        is ``True``.

        :returns: The `Paste` for `id` or None, if there is no such paste
        :returntype: `Paste`"""
        if self.caching and id in self._cache:
            return self._cache[id]
        else:
            return self._get_paste_from_result(
                self._lodgeit.pastes.getPaste(id))

    def get_last_paste(self):
        """Returns the last paste. This method is never cached.

        :returntype: `Paste`"""
        return self._get_paste_from_result(self._lodgeit.pastes.getLast())

    def get_recent_pastes(self, amount=5):
        """Returns the most recent pastes.

        :returntype: [`Paste`, `Paste`, ...]"""
        pastes = self._lodgeit.pastes.getRecent(amount)
        return map(self._get_paste_from_result, pastes)

    @property
    def languages(self):
        """The languages supported by the paste bin. It maps the language
        identifier to a short description.

        :type: dict, mapping the language identifier to a short description
        """
        if not self.has_languages:
            self._languages = dict(self._lodgeit.pastes.getLanguages())
        return self._languages

    @property
    def has_languages(self):
        """``True``, if the internal language cache is filled, ``False``
        otherwise.
        """
        return bool(self._languages)

    def reset_languages(self):
        """Clears the internal language cache. You should normally not need
        this.
        """
        self._languages = None

    def new_paste(self, code, language, parent=None, filename='',
                  mimetype=''):
        """Creates a new paste. `code` is the pasted code, `language` the
        language of the code, which is used for server-side highlighting.

        `parent` is the parent paste. This may either be an integer, or a
        `Paste` object. This argument provides access to the \"paste reply\"
        functionality of the Lodgeit, which is described in detail under
        `Advanced features`_.

        `filename` and `mimetype` are used for guessing the correct
        language, if `language` is None.

        Returns the id of the created paste.

        _`Advanced features`: http://paste.pocoo.org/help/advanced/

        :param code: The pasted code
        :param language: The language of the paste. May be ``None``, in
                         which case the language is guessed from the
                         `filename` and/or `mimetype` arguments

        :keyword parent: The parent paste
        :keyword filename: The name of the file from which the paste code
                           was read. Used only for language guessing and is
                           only evaluted, if `language` is ``None``.
        :keyword mimetype: The mimetype of the code. Used only for language
                           guessing and is only evaluated, if `language` is
                           ``None``.

        :type code: `unicode`
        :type language: `str` or `unicode`
        :type parent: Integer or `Paste` object
        :type filename: `str` or `unicode`
        :type mimetype: `str` or `unicode`

        :returns: The id of the created paste
        :returntype: Integer

        :raises UnsupportedLanguageError: If `language` is not supported,
                                          e.g. not in `languages`
        """
        if not isinstance(code, unicode):
            raise TypeError('code must be unicode')

        if language and language not in self.languages:
            raise UnsupportedLanguageError(language)

        parent_id = (parent.id if isinstance(parent, Paste) else parent)
        return self._lodgeit.pastes.newPaste(language, code, parent_id,
                                             filename, mimetype)


lodgeit = Lodgeit()
