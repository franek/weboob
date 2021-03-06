# -*- coding: utf-8 -*-

# Copyright(C) 2011 Laurent Bachelier
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


from __future__ import with_statement

from weboob.capabilities.paste import ICapPaste


class BasePasteBackend(ICapPaste):
    EXPIRATIONS = {}
    """
    List of expirations and their corresponding remote codes (any type can be used).
    The expirations, i.e. the keys, are integers representing the duration
    in seconds. There also can be one False key, for the "forever" expiration.
    """

    def get_closest_expiration(self, max_age):
        """
        Get the expiration closest (and less or equal to) max_age (int, in seconds).
        max_age set to False means we want it to never expire.

        @return int or False if found, else None
        """
        # "forever"
        if max_age is False and False in self.EXPIRATIONS:
            return max_age
        # get timed expirations, longest first
        expirations = sorted([e for e in self.EXPIRATIONS if e is not False], reverse=True)
        # find the first expiration that is below or equal to the maximum wanted age
        for e in expirations:
            if max_age is False or max_age >= e:
                return e


def test():
    class MockPasteBackend(BasePasteBackend):
        def __init__(self, expirations):
            self.EXPIRATIONS = expirations

    # all expirations are too high
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(1) is None
    # we found a suitable lower or equal expiration
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(84) is 42
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(False) is False
    assert MockPasteBackend({1337: '', 42: ''}).get_closest_expiration(False) is 1337
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(1336) is 42
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(1337) is 1337
    assert MockPasteBackend({1337: '', 42: '', False: ''}).get_closest_expiration(1338) is 1337
    # this format should work, though of doubtful usage
    assert MockPasteBackend([1337, 42, False]).get_closest_expiration(84) is 42
