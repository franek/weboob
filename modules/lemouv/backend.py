# * -*- coding: utf-8 -*-

# Copyright(C) 2011  Johann Broudin
#
# This file is part of weboob.
#
# weboob is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# weboob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with weboob. If not, see <http://www.gnu.org/licenses/>.


from weboob.capabilities.radio import ICapRadio, Radio, Stream, Emission
from weboob.capabilities.collection import ICapCollection, CollectionNotFound
from weboob.tools.backend import BaseBackend
from weboob.tools.browser import BaseBrowser, BasePage


__all__ = ['LeMouvBackend']


class XMLinfos(BasePage):
    def get_current(self):
        try:
            for channel in self.parser.select(self.document.getroot(), 'channel'):
                title = channel.find('item/song_title').text
                artist = channel.find('item/artist_name').text
        except AttributeError:
            title = "Not defined"
            artist = "Not defined"

        return unicode(artist).strip(), unicode(title).strip()

class LeMouvBrowser(BaseBrowser):
    DOMAIN = u'statique.lemouv.fr'
    PAGES  = {r'.*/files/rfPlayer/mouvRSS\.xml': XMLinfos}

    def get_current(self, radio):
        self.location('/files/rfPlayer/mouvRSS.xml')
        assert self.is_on_page(XMLinfos)

        return self.page.get_current()

class LeMouvBackend(BaseBackend, ICapRadio, ICapCollection):
    NAME = 'lemouv'
    MAINTAINER = 'Johann Broudin'
    EMAIL = 'johann.broudin@6-8.fr'
    VERSION = '0.a'
    DESCRIPTION = u'The le mouv\' french radio'
    LICENCE = 'AGPLv3+'
    BROWSER = LeMouvBrowser

    _RADIOS = {'lemouv': (u'le mouv\'', u'le mouv', u'http://mp3.live.tv-radio.com/lemouv/all/lemouvhautdebit.mp3')}

    def iter_resources(self, splited_path):
        if len(splited_path) > 0:
            raise CollectionNotFound()

        for id in self._RADIOS.iterkeys():
            yield self.get_radio(id)

    def iter_radios_search(self, pattern):
        for radio in self.iter_resources([]):
            if pattern.lower() in radio.title.lower() or pattern.lower() in radio.description.lower():
                yield radio

    def get_radio(self, radio):
        if not isinstance(radio, Radio):
            radio = Radio(radio)

        if not radio.id in self._RADIOS:
            return None

        title, description, url = self._RADIOS[radio.id]
        radio.title = title
        radio.description = description

        artist, title = self.browser.get_current(radio.id)
        current = Emission(0)
        current.artist = artist
        current.title = title
        radio.current = current

        stream = Stream(0)
        stream.title = u'128kbits/s'
        stream.url = url
        radio.streams = [stream]
        return radio

    def fill_radio(self, radio, fields):
        if 'current' in fields:
            if not radio.current:
                radio.current = Emission(0)
            radio.current.artist, radio.current.title = self.browser.get_current(radio.id)
        return radio

    OBJECTS = {Radio: fill_radio}