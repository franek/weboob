# -*- coding: utf-8 -*-

# Copyright(C) 2008-2011  Romain Bignon, Christophe Benz
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


import math
import re
import datetime
import random
import urllib
try:
    import json
except ImportError:
    import simplejson as json

from weboob.tools.browser import BaseBrowser, BrowserIncorrectPassword, BrowserUnavailable

from weboob.capabilities.chat import ChatException, ChatMessage
from weboob.capabilities.messages import CantSendMessage


__all__ = ['AuMBrowser']


class AuMBrowser(BaseBrowser):
    DOMAIN = 'api.adopteunmec.com'
    APIKEY = 'fb0123456789abcd'

    consts = None
    search_query = None
    my_sex = 0
    my_id = 0
    my_name = u''
    my_coords = (0,0)

    def id2url(self, id):
        return 'http://www.adopteunmec.com/%s' % id

    def api_request(self, command, action, parameter='', data=None, nologin=False):
        if data is None:
            # Always do POST requests.
            data = ''
        elif isinstance(data, (list,tuple,dict)):
            data = urllib.urlencode(data)
        elif isinstance(data, unicode):
            data = data.encode('utf-8')

        url = self.buildurl(self.absurl('/api.php'), S=self.APIKEY,
                                                     C=command,
                                                     A=action,
                                                     P=parameter,
                                                     O='json')
        buf = self.openurl(url, data)

        try:
            r = json.load(buf)
        except ValueError:
            buf.seek(0)
            raise ValueError(buf.read())

        if 'errors' in r and len(r['errors']) > 0 and r['errors'][0] in (u'0.0.2', u'1.1.1'):
            if not nologin:
                self.login()
                return self.api_request(command, action, parameter, data, nologin=True)
            else:
                raise BrowserIncorrectPassword()
        return r

    def login(self):
        r = self.api_request('me', 'login', data={'login': self.username,
                                                  'pass':  self.password,
                                                 }, nologin=True)
        self.my_sex = r['result']['me']['sex']
        self.my_id = int(r['result']['me']['id'])
        self.my_name = r['result']['me']['pseudo']
        self.my_coords = (float(r['result']['me']['lat']), float(r['result']['me']['lng']))
        return r

    #def register(self, password, sex, birthday_d, birthday_m, birthday_y, zipcode, country, godfather=None):
    #    if not self.is_on_page(RegisterPage):
    #        self.location('http://www.adopteunmec.com/register2.php')
    #    self.page.register(password, sex, birthday_d, birthday_m, birthday_y, zipcode, country)
    #    if godfather:
    #        if not self.is_on_page(AccountPage):
    #            self.location('http://www.adopteunmec.com/account.php')
    #        self.page.set_godfather(godfather)

    #@pageaccess
    #def add_photo(self, name, f):
    #    if not self.is_on_page(EditPhotoPage):
    #        self.location('/edit.php?type=1')
    #    return self.page.add_photo(name, f)

    #@pageaccess
    #def set_nickname(self, nickname):
    #    if not self.is_on_page(EditAnnouncePage):
    #        self.location('/edit.php?type=2')
    #    return self.page.set_nickname(nickname)

    #@pageaccess
    #def set_announce(self, title=None, description=None, lookingfor=None):
    #    if not self.is_on_page(EditAnnouncePage):
    #        self.location('/edit.php?type=2')
    #    return self.page.set_announce(title, description, lookingfor)

    #@pageaccess
    #def set_description(self, **args):
    #    if not self.is_on_page(EditDescriptionPage):
    #        self.location('/edit.php?type=3')
    #    return self.page.set_description(**args)

    def check_login(func):
        def inner(self, *args, **kwargs):
            if self.my_id == 0:
                self.login()
            return func(self, *args, **kwargs)
        return inner

    def get_consts(self):
        if self.consts is not None:
            return self.consts

        self.consts = []
        for i in xrange(2):
            r = self.api_request('me', 'all_values', data={'sex': i})
            self.consts.append(r['result']['values'])

        return self.consts

    @check_login
    def score(self):
        r = self.api_request('member', 'view', data={'id': self.my_id})
        return int(r['result']['member']['popu']['popu'])

    @check_login
    def get_my_name(self):
        return self.my_name

    @check_login
    def get_my_id(self):
        return self.my_id

    @check_login
    def nb_new_mails(self):
        r = self.api_request('me', '[default]')
        return r['result']['news']['newMails']

    @check_login
    def nb_new_baskets(self):
        r = self.api_request('me', '[default]')
        return r['result']['news']['newBaskets']

    @check_login
    def nb_new_visites(self):
        r = self.api_request('me', '[default]')
        return r['result']['news']['newVisits']

    @check_login
    def nb_available_charms(self):
        r = self.login()
        return r['result']['flashs']

    @check_login
    def nb_godchilds(self):
        r = self.api_request('member', 'view', data={'id': self.my_id})
        return int(r['result']['member']['popu']['invits'])

    @check_login
    def get_baskets(self):
        r = self.api_request('me', 'basket')
        return r['result']['basket']

    @check_login
    def get_threads_list(self, count=30):
        r = self.api_request('message', '[default]', '%d,0' % count)
        return r['result']['threads']

    @check_login
    def get_thread_mails(self, id, count=30):
        r = self.api_request('message', 'thread', data={'memberId': id, 'count': count})
        return r['result']['thread']

    @check_login
    def post_mail(self, id, content):
        r = self.api_request('message', 'new', data={'memberId': id, 'message': content.encode('utf-8')})
        if len(r['errors']) > 0:
            raise CantSendMessage(r['errors'][0])

    @check_login
    def delete_thread(self, id):
        r = self.api_request('message', 'delete', data={'id_user': id})
        self.logger.debug('Thread deleted: %r' % r)

    @check_login
    def send_charm(self, id):
        r = self.api_request('member', 'addBasket', data={'id': id})
        return r['errors'] == '0'

    @check_login
    def add_basket(self, id):
        r = self.api_request('member', 'addBasket', data={'id': id})
        return r['errors'] == '0'

    def deblock(self, id):
        self.readurl('http://www.adopteunmec.com/fajax_postMessage.php?action=deblock&to=%s' % id)
        return True

    def report_fake(self, id):
        return self.readurl('http://www.adopteunmec.com/fake.php', 'id=%s' % id)

    def rate(self, id, what, rating):
        result = self.openurl('http://www.adopteunmec.com/fajax_vote.php', 'member=%s&what=%s&rating=%s' % (id, what, rating)).read()
        return float(result)

    def search_profiles(self, **kwargs):
        if self.search_query is None:
            r = self.api_request('searchs', '[default]')
            self.search_query = r['result']['search']['query']

        params = json.loads(self.search_query)
        r = self.api_request('searchs', 'advanced', '30,0', params)
        ids = [s['id'] for s in r['result']['search']]
        return set(ids)

    def get_profile(self, id, with_pics=True):
        r = self.api_request('member', 'view', data={'id': id})
        profile = r['result']['member']


        # Calculate distance in km.
        coords = (float(profile['lat']), float(profile['lng']))

        R = 6371
        lat1 = math.radians(self.my_coords[0])
        lat2 = math.radians(coords[0])
        lon1 = math.radians(self.my_coords[1])
        lon2 = math.radians(coords[1])
        dLat = lat2 - lat1
        dLong = lon2 - lon1
        a= pow(math.sin(dLat/2), 2) + math.cos(lat1) * math.cos(lat2) * pow(math.sin(dLong/2), 2)
        c= 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        profile['dist'] = R * c

        if with_pics:
            r = self.api_request('member', 'pictures', data={'id': id})
            profile['pictures'] = []
            for pic in r['result']['pictures']:
                d = {'hidden': False}
                d.update(pic)
                profile['pictures'].append(d)

            if len(profile['pictures']) > 0:
                pic_regex = re.compile('(?P<base_url>http://.+\.adopteunmec\.com/.+/)image(?P<id>.+)\.jpg')
                pic_max_id = max(int(pic_regex.match(pic['url']).groupdict()['id']) for pic in profile['pictures'])
                base_url = pic_regex.match(profile['pictures'][0]['url']).groupdict()['base_url']
                for id in xrange(1, pic_max_id + 1):
                    url = u'%simage%s.jpg' % (base_url, id)
                    if not url in [pic['url'] for pic in profile['pictures']]:
                        profile['pictures'].append({'url': url, u'hidden': True, 'id': u'0', 'rating': 0.0})

        return profile

    def _get_chat_infos(self):
        try:
            data = json.load(self.openurl('http://www.adopteunmec.com/1.1_cht_get.php?anticache=%f' % random.random()))
        except ValueError:
            raise BrowserUnavailable()

        if data['error']:
            raise ChatException(u'Error while getting chat infos. json:\n%s' % data)
        return data

    def iter_contacts(self):
        def iter_dedupe(contacts):
            yielded_ids = set()
            for contact in contacts:
                if contact['id'] not in yielded_ids:
                    yield contact
                yielded_ids.add(contact['id'])

        data = self._get_chat_infos()
        return iter_dedupe(data['contacts'])

    def iter_chat_messages(self, _id=None):
        data = self._get_chat_infos()
        if data['messages'] is not None:
            for message in data['messages']:
                yield ChatMessage(id_from=message['id_from'], id_to=message['id_to'], message=message['message'], date=message['date'])

    def send_chat_message(self, _id, message):
        url = 'http://www.adopteunmec.com/1.1_cht_send.php?anticache=%f' % random.random()
        data = dict(id=_id, message=message)
        headers = {
                'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'text/plain',
                'Referer': 'http://www.adopteunmec.com/chat.php',
                'Origin': 'http://www.adopteunmec.com',
                }
        request = self.request_class(url, urllib.urlencode(data), headers)
        response = self.openurl(request).read()
        try:
            datetime.datetime.strptime(response,  '%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False
