# -*- coding: utf-8 -*-

# Copyright(C) 2013 Julien Veyssier
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

import sys
from datetime import datetime

from weboob.applications.weboorrents.weboorrents import TorrentInfoFormatter, TorrentListFormatter
from weboob.applications.suboob.suboob import SubtitleInfoFormatter, SubtitleListFormatter
from weboob.capabilities.torrent import ICapTorrent, MagnetOnly
from weboob.capabilities.cinema import ICapCinema
from weboob.capabilities.subtitle import ICapSubtitle
from weboob.capabilities.base import empty
from weboob.tools.application.repl import ReplApplication
from weboob.tools.application.formatters.iformatter import IFormatter, PrettyFormatter
from weboob.core import CallErrors


__all__ = ['Cineoob']

ROLE_LIST = ['actor', 'director', 'writer', 'composer', 'producer']
COUNTRY_LIST = ['us', 'fr', 'de', 'jp']


class MovieInfoFormatter(IFormatter):
    MANDATORY_FIELDS = ('id', 'original_title', 'release_date',
                        'other_titles', 'duration', 'pitch', 'note', 'roles', 'country')

    def format_obj(self, obj, alias):
        result = u'%s%s%s\n' % (self.BOLD, obj.original_title, self.NC)
        result += 'ID: %s\n' % obj.fullid
        if not empty(obj.release_date):
            result += 'Released: %s\n' % obj.release_date.strftime('%Y-%m-%d')
        result += 'Country: %s\n' % obj.country
        if not empty(obj.duration):
            result += 'Duration: %smin\n' % obj.duration
        result += 'Note: %s\n' % obj.note
        if not empty(obj.genres):
            result += '\n%sGenres%s\n' % (self.BOLD, self.NC)
            for g in obj.genres:
                result += ' * %s\n' % g
        if not empty(obj.roles):
            result += '\n%sRelated persons%s\n' % (self.BOLD, self.NC)
            for role, lpersons in obj.roles.items():
                result += ' -- %s\n' % role
                for name in lpersons:
                    result += '   * %s\n' % name
        if not empty(obj.other_titles):
            result += '\n%sOther titles%s\n' % (self.BOLD, self.NC)
            for t in obj.other_titles:
                result += ' * %s\n' % t
        if not empty(obj.pitch):
            result += '\n%sStory%s\n' % (self.BOLD, self.NC)
            result += '%s' % obj.pitch
        return result


class MovieListFormatter(PrettyFormatter):
    MANDATORY_FIELDS = ('id', 'original_title', 'short_description')

    def get_title(self, obj):
        return obj.original_title

    def get_description(self, obj):
        result = u''
        if not empty(obj.short_description):
            result = obj.short_description
        return result


class MovieReleasesFormatter(PrettyFormatter):
    MANDATORY_FIELDS = ('id', 'original_title', 'all_release_dates')

    def get_title(self, obj):
        return u'Releases of %s' % obj.original_title

    def get_description(self, obj):
        return u'\n%s' % obj.all_release_dates


def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except:
        # Must be 2/29
        assert from_date.month == 2 and from_date.day == 29
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)


def num_years(begin, end=None):
    if end is None:
        end = datetime.now()
    num_years = int((end - begin).days / 365.25)
    if begin > yearsago(num_years, end):
        return num_years - 1
    else:
        return num_years


class PersonInfoFormatter(IFormatter):
    MANDATORY_FIELDS = ('id', 'name', 'birth_date', 'birth_place', 'short_biography')

    def format_obj(self, obj, alias):
        result = u'%s%s%s\n' % (self.BOLD, obj.name, self.NC)
        result += 'ID: %s\n' % obj.fullid
        if not empty(obj.real_name):
            result += 'Real name: %s\n' % obj.real_name
        if not empty(obj.birth_place):
            result += 'Birth place: %s\n' % obj.birth_place
        if not empty(obj.birth_date):
            result += 'Birth date: %s\n' % obj.birth_date.strftime('%Y-%m-%d')
            if not empty(obj.death_date):
                age = num_years(obj.birth_date, obj.death_date)
                result += 'Death date: %s at %s years old\n' % (obj.death_date.strftime('%Y-%m-%d'), age)
            else:
                age = num_years(obj.birth_date)
                result += 'Age: %s\n' % age
        if not empty(obj.gender):
            result += 'Gender: %s\n' % obj.gender
        if not empty(obj.nationality):
            result += 'Nationality: %s\n' % obj.nationality
        if not empty(obj.roles):
            result += '\n%sRelated movies%s\n' % (self.BOLD, self.NC)
            for role, lmovies in obj.roles.items():
                result += ' -- %s\n' % role
                for movie in lmovies:
                    result += '   * %s\n' % movie
        if not empty(obj.short_biography):
            result += '\n%sShort biography%s\n' % (self.BOLD, self.NC)
            result += '%s' % obj.short_biography
        return result


class PersonListFormatter(PrettyFormatter):
    MANDATORY_FIELDS = ('id', 'name', 'short_description')

    def get_title(self, obj):
        return obj.name

    def get_description(self, obj):
        result = u''
        if not empty(obj.short_description):
            result = obj.short_description
        return result


class PersonBiographyFormatter(PrettyFormatter):
    MANDATORY_FIELDS = ('id', 'name', 'biography')

    def get_title(self, obj):
        return u'Biography of %s' % obj.name

    def get_description(self, obj):
        result = u'\n%s' % obj.biography
        return result


class Cineoob(ReplApplication):
    APPNAME = 'cineoob'
    VERSION = '0.f'
    COPYRIGHT = 'Copyright(C) 2013 Julien Veyssier'
    DESCRIPTION = "Console application allowing to search for movies and persons on various cinema databases " \
                  ", list persons related to a movie, list movies related to a person and list common movies " \
                  "of two persons."
    SHORT_DESCRIPTION = "search movies and persons around cinema"
    CAPS = (ICapCinema, ICapTorrent, ICapSubtitle)
    EXTRA_FORMATTERS = {'movie_list': MovieListFormatter,
                        'movie_info': MovieInfoFormatter,
                        'movie_releases': MovieReleasesFormatter,
                        'person_list': PersonListFormatter,
                        'person_info': PersonInfoFormatter,
                        'person_bio': PersonBiographyFormatter,
                        'torrent_list': TorrentListFormatter,
                        'torrent_info': TorrentInfoFormatter,
                        'subtitle_list': SubtitleListFormatter,
                        'subtitle_info': SubtitleInfoFormatter
                        }
    COMMANDS_FORMATTERS = {'search_movie':    'movie_list',
                           'info_movie':      'movie_info',
                           'search_person':   'person_list',
                           'info_person':     'person_info',
                           'casting':         'person_list',
                           'filmography':     'movie_list',
                           'biography':     'person_bio',
                           'releases':     'movie_releases',
                           'movies_in_common': 'movie_list',
                           'persons_in_common': 'person_list',
                           'search_torrent':    'torrent_list',
                           'search_movie_torrent':    'torrent_list',
                           'info_torrent':      'torrent_info',
                           'search_subtitle':    'subtitle_list',
                           'search_movie_subtitle':    'subtitle_list',
                           'info_subtitle':      'subtitle_info'
                           }

    def complete_filmography(self, text, line, *ignored):
        args = line.split(' ')
        if len(args) == 3:
            return ROLE_LIST

    def complete_casting(self, text, line, *ignored):
        return self.complete_filmography(text, line, ignored)

    def do_movies_in_common(self, line):
        """
        movies_in_common  person_ID  person_ID

        Get the list of common movies between two persons.
        """
        id1, id2 = self.parse_command_args(line, 2, 1)

        person1 = self.get_object(id1, 'get_person')
        if not person1:
            print >>sys.stderr, 'Person not found: %s' % id1
            return 3
        person2 = self.get_object(id2, 'get_person')
        if not person2:
            print >>sys.stderr, 'Person not found: %s' % id2
            return 3

        initial_count = self.options.count
        self.options.count = None

        lid1 = []
        for backend, id in self.do('iter_person_movies_ids', person1.id, caps=ICapCinema):
            lid1.append(id)
        self.flush()
        lid2 = []
        for backend, id in self.do('iter_person_movies_ids', person2.id, caps=ICapCinema):
            lid2.append(id)
        self.flush()
        self.options.count = initial_count
        inter = list(set(lid1) & set(lid2))
        for common in inter:
            movie = self.get_object(common, 'get_movie')
            if movie:
                self.cached_format(movie)
        self.flush()

    def do_persons_in_common(self, line):
        """
        persons_in_common  movie_ID  movie_ID

        Get the list of common persons between two movies.
        """
        id1, id2 = self.parse_command_args(line, 2, 1)
        self.flush()

        movie1 = self.get_object(id1, 'get_movie')
        if not movie1:
            print >>sys.stderr, 'Movie not found: %s' % id1
            return 3
        movie2 = self.get_object(id2, 'get_movie')
        if not movie2:
            print >>sys.stderr, 'Movie not found: %s' % id2
            return 3

        initial_count = self.options.count
        self.options.count = None

        lid1 = []
        for backend, id in self.do('iter_movie_persons_ids', movie1.id, caps=ICapCinema):
            lid1.append(id)
        self.flush()
        lid2 = []
        for backend, id in self.do('iter_movie_persons_ids', movie2.id, caps=ICapCinema):
            lid2.append(id)
        self.flush()
        self.options.count = initial_count
        inter = list(set(lid1) & set(lid2))
        for common in inter:
            person = self.get_object(common, 'get_person')
            self.cached_format(person)
        self.flush()

    def do_info_movie(self, id):
        """
        info_movie  movie_ID

        Get information about a movie.
        """
        movie = self.get_object(id, 'get_movie')

        if not movie:
            print >>sys.stderr, 'Movie not found: %s' % id
            return 3

        self.start_format()
        self.format(movie)
        self.flush()

    def do_info_person(self, id):
        """
        info_person  person_ID

        Get information about a person.
        """
        person = self.get_object(id, 'get_person')

        if not person:
            print >>sys.stderr, 'Person not found: %s' % id
            return 3

        self.start_format()
        self.format(person)
        self.flush()

    def do_search_movie(self, pattern):
        """
        search_movie  [PATTERN]

        Search movies.
        """
        self.change_path([u'search movies'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, movie in self.do('iter_movies', pattern=pattern, caps=ICapCinema):
            self.cached_format(movie)
        self.flush()

    def do_search_person(self, pattern):
        """
        search_person  [PATTERN]

        Search persons.
        """
        self.change_path([u'search persons'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, person in self.do('iter_persons', pattern=pattern, caps=ICapCinema):
            self.cached_format(person)
        self.flush()

    def do_casting(self, line):
        """
        casting  movie_ID  [ROLE]

        List persons related to a movie.
        If ROLE is given, filter by ROLE
        """
        movie_id, role = self.parse_command_args(line, 2, 1)

        movie = self.get_object(movie_id, 'get_movie')
        if not movie:
            print >>sys.stderr, 'Movie not found: %s' % id
            return 3

        for backend, person in self.do('iter_movie_persons', movie.id, role, caps=ICapCinema):
            self.cached_format(person)
        self.flush()

    def do_filmography(self, line):
        """
        filmography  person_ID  [ROLE]

        List movies of a person.
        If ROLE is given, filter by ROLE
        """
        person_id, role = self.parse_command_args(line, 2, 1)

        person = self.get_object(person_id, 'get_person')
        if not person:
            print >>sys.stderr, 'Person not found: %s' % id
            return 3

        for backend, movie in self.do('iter_person_movies', person.id, role, caps=ICapCinema):
            self.cached_format(movie)
        self.flush()

    def do_biography(self, person_id):
        """
        biography  person_ID

        Show the complete biography of a person.
        """
        person = self.get_object(person_id, 'get_person', ('name', 'biography'))
        if not person:
            print >>sys.stderr, 'Person not found: %s' % person_id
            return 3

        self.start_format()
        self.format(person)
        self.flush()

    def complete_releases(self, text, line, *ignored):
        args = line.split(' ')
        if len(args) == 3:
            return self.COUNTRY_LIST

    def do_releases(self, line):
        """
        releases  movie_ID [COUNTRY]

        Get releases dates of a movie.
        If COUNTRY is given, show release in this country.
        """
        id, country = self.parse_command_args(line, 2, 1)

        movie = self.get_object(id, 'get_movie', ('original_title'))
        if not movie:
            print >>sys.stderr, 'Movie not found: %s' % id
            return 3

        # i would like to clarify with fillobj but how could i fill the movie AND choose the country ?
        for backend, release in self.do('get_movie_releases', movie.id, country, caps=ICapCinema):
            if not empty(release):
                movie.all_release_dates = u'%s' % (release)
            else:
                print >>sys.stderr, 'Movie releases not found: %s' % id
                return 3
        self.start_format()
        self.format(movie)
        self.flush()

    #================== TORRENT ==================

    def complete_info_torrent(self, text, line, *ignored):
        args = line.split(' ')
        if len(args) == 2:
            return self._complete_object()

    def do_info_torrent(self, id):
        """
        info_torrent ID

        Get information about a torrent.
        """

        torrent = self.get_object(id, 'get_torrent')
        if not torrent:
            print >>sys.stderr, 'Torrent not found: %s' % id
            return 3

        self.start_format()
        self.format(torrent)
        self.flush()

    def complete_getfile_torrent(self, text, line, *ignored):
        args = line.split(' ', 2)
        if len(args) == 2:
            return self._complete_object()
        elif len(args) >= 3:
            return self.path_completer(args[2])

    def do_getfile_torrent(self, line):
        """
        getfile_torrent ID [FILENAME]

        Get the .torrent file.
        FILENAME is where to write the file. If FILENAME is '-',
        the file is written to stdout.
        """
        id, dest = self.parse_command_args(line, 2, 1)

        _id, backend_name = self.parse_id(id)

        if dest is None:
            dest = '%s.torrent' % _id

        try:
            for backend, buf in self.do('get_torrent_file', _id, backends=backend_name, caps=ICapTorrent):
                if buf:
                    if dest == '-':
                        print buf
                    else:
                        try:
                            with open(dest, 'w') as f:
                                f.write(buf)
                        except IOError, e:
                            print >>sys.stderr, 'Unable to write .torrent in "%s": %s' % (dest, e)
                            return 1
                    return
        except CallErrors, errors:
            for backend, error, backtrace in errors:
                if isinstance(error, MagnetOnly):
                    print >>sys.stderr, u'Error(%s): No direct URL available, ' \
                        u'please provide this magnet URL ' \
                        u'to your client:\n%s' % (backend, error.magnet)
                    return 4
                else:
                    self.bcall_error_handler(backend, error, backtrace)

        print >>sys.stderr, 'Torrent "%s" not found' % id
        return 3

    def do_search_torrent(self, pattern):
        """
        search_torrent [PATTERN]

        Search torrents.
        """
        self.change_path([u'search torrent'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, torrent in self.do('iter_torrents', pattern=pattern, caps=ICapTorrent):
            self.cached_format(torrent)
        self.flush()

    def do_search_movie_torrent(self, id):
        """
        search_movie_torrent movie_ID

        Search torrents of movie_ID.
        """
        movie = self.get_object(id, 'get_movie', ('original_title'))
        if not movie:
            print >>sys.stderr, 'Movie not found: %s' % id
            return 3

        pattern = movie.original_title

        self.change_path([u'search torrent'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, torrent in self.do('iter_torrents', pattern=pattern, caps=ICapTorrent):
            self.cached_format(torrent)
        self.flush()

    #================== SUBTITLE ==================

    def complete_info_subtitle(self, text, line, *ignored):
        args = line.split(' ')
        if len(args) == 2:
            return self._complete_object()

    def do_info_subtitle(self, id):
        """
        info_subtitle subtitle_ID

        Get information about a subtitle.
        """

        subtitle = self.get_object(id, 'get_subtitle')
        if not subtitle:
            print >>sys.stderr, 'Subtitle not found: %s' % id
            return 3

        self.start_format()
        self.format(subtitle)
        self.flush()

    def complete_getfile_subtitle(self, text, line, *ignored):
        args = line.split(' ', 2)
        if len(args) == 2:
            return self._complete_object()
        elif len(args) >= 3:
            return self.path_completer(args[2])

    def do_getfile_subtitle(self, line):
        """
        getfile_subtitle subtitle_ID [FILENAME]

        Get the subtitle or archive file.
        FILENAME is where to write the file. If FILENAME is '-',
        the file is written to stdout.
        """
        id, dest = self.parse_command_args(line, 2, 1)

        _id, backend_name = self.parse_id(id)

        if dest is None:
            dest = '%s' % _id

        try:
            for backend, buf in self.do('get_subtitle_file', _id, backends=backend_name, caps=ICapSubtitle):
                if buf:
                    if dest == '-':
                        print buf
                    else:
                        try:
                            with open(dest, 'w') as f:
                                f.write(buf)
                        except IOError, e:
                            print >>sys.stderr, 'Unable to write file in "%s": %s' % (dest, e)
                            return 1
                    return
        except CallErrors, errors:
            for backend, error, backtrace in errors:
                self.bcall_error_handler(backend, error, backtrace)

        print >>sys.stderr, 'Subtitle "%s" not found' % id
        return 3

    def do_search_subtitle(self, line):
        """
        search_subtitle language [PATTERN]

        Search subtitles.
        """
        language, pattern = self.parse_command_args(line, 2, 1)
        self.change_path([u'search subtitle'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, subtitle in self.do('iter_subtitles', language=language, pattern=pattern, caps=ICapSubtitle):
            self.cached_format(subtitle)
        self.flush()

    def do_search_movie_subtitle(self, line):
        """
        search_movie_subtitle language movie_ID

        Search subtitles of movie_ID.
        """
        language, id = self.parse_command_args(line, 2, 2)
        movie = self.get_object(id, 'get_movie', ('original_title'))
        if not movie:
            print >>sys.stderr, 'Movie not found: %s' % id
            return 3

        pattern = movie.original_title
        self.change_path([u'search subtitle'])
        if not pattern:
            pattern = None

        self.start_format(pattern=pattern)
        for backend, subtitle in self.do('iter_subtitles', language=language, pattern=pattern, caps=ICapSubtitle):
            self.cached_format(subtitle)
        self.flush()
