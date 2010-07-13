# -*- coding: utf-8 -*-

# Copyright(C) 2010  Roger Philibert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import re

from weboob.tools.browser import BasePage, ExpectedElementNotFound

from ..video import YoujizzVideo


__all__ = ['IndexPage']


class IndexPage(BasePage):
    def iter_videos(self):
        div_id = 'span#miniatura'
        span_list = self.document.getroot().cssselect(div_id)
        if not span_list:
            raise ExpectedElementNotFound(div_id)

        for span in span_list:
            a = span.find('.//a')
            if a is None:
                raise ExpectedElementNotFound('%s.//a' % span)
            url = a.attrib['href']
            _id = re.sub(r'/videos/(.+)\.html', r'\1', url)

            thumbnail_url = span.find('.//img').attrib['src']

            title1_selector = 'span#title1'
            title1 = span.cssselect(title1_selector)
            if title1 is None:
                raise ExpectedElementNotFound(title1_selector)
            title = title1[0].text.strip()

            thumbtime = span.cssselect('span.thumbtime')
            minutes = seconds = 0
            if thumbtime is not None:
                time_span = thumbtime[0].find('span')
                minutes, seconds = (int(v) for v in time_span.text.strip().split(':'))

            yield YoujizzVideo(_id,
                               title=title,
                               duration=datetime.timedelta(minutes=minutes, seconds=seconds),
                               thumbnail_url=thumbnail_url,
                               )
