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

import urllib

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QFrame, QImage, QPixmap

from weboob.applications.qcineoob.ui.movie_ui import Ui_Movie
from weboob.capabilities.base import empty
from weboob.applications.suboob.suboob import LANGUAGE_CONV


class Movie(QFrame):
    def __init__(self, movie, backend, parent=None):
        QFrame.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_Movie()
        self.ui.setupUi(self)
        langs = LANGUAGE_CONV.keys()
        langs.sort()
        for lang in langs:
            self.ui.langCombo.addItem(lang)

        self.connect(self.ui.castingButton, SIGNAL("clicked()"), self.casting)
        self.connect(self.ui.torrentButton, SIGNAL("clicked()"), self.searchTorrent)
        self.connect(self.ui.subtitleButton, SIGNAL("clicked()"), self.searchSubtitle)

        self.movie = movie
        self.backend = backend
        self.ui.titleLabel.setText(movie.original_title)
        self.ui.durationLabel.setText(unicode(movie.duration))
        self.gotThumbnail()
        self.putReleases()

        self.ui.idEdit.setText(u'%s@%s' % (movie.id, backend.name))
        if not empty(movie.other_titles):
            self.ui.otherTitlesPlain.setPlainText('\n'.join(movie.other_titles))
        else:
            self.ui.otherTitlesPlain.parent().hide()
        if not empty(movie.genres):
            genres = u''
            for g in movie.genres:
                genres += '%s, ' % g
            genres = genres[:-2]
            self.ui.genresLabel.setText(genres)
        else:
            self.ui.genresLabel.parent().hide()
        if not empty(movie.release_date):
            self.ui.releaseDateLabel.setText(movie.release_date.strftime('%Y-%m-%d'))
        else:
            self.ui.releaseDateLabel.parent().hide()
        if not empty(movie.duration):
            self.ui.durationLabel.setText('%s min' % movie.duration)
        else:
            self.ui.durationLabel.parent().hide()
        if not empty(movie.pitch):
            self.ui.pitchPlain.setPlainText('%s' % movie.pitch)
        else:
            self.ui.pitchPlain.parent().hide()
        if not empty(movie.country):
            self.ui.countryLabel.setText('%s' % movie.country)
        else:
            self.ui.countryLabel.parent().hide()
        if not empty(movie.note):
            self.ui.noteLabel.setText('%s' % movie.note)
        else:
            self.ui.noteLabel.parent().hide()
        for role in movie.roles.keys():
            self.ui.castingCombo.addItem('%s' % role)

        self.ui.verticalLayout.setAlignment(Qt.AlignTop)
        self.ui.verticalLayout_2.setAlignment(Qt.AlignTop)

    def putReleases(self):
        rel = self.backend.get_movie_releases(self.movie.id)
        if not empty(rel):
            self.ui.allReleasesPlain.setPlainText(rel)
        else:
            self.ui.allReleasesPlain.parent().hide()

    def gotThumbnail(self):
        if not empty(self.movie.thumbnail_url):
            data = urllib.urlopen(self.movie.thumbnail_url).read()
            img = QImage.fromData(data)
            self.ui.imageLabel.setPixmap(QPixmap.fromImage(img).scaledToWidth(220,Qt.SmoothTransformation))

    def searchSubtitle(self):
        tosearch = unicode(self.movie.original_title)
        lang = unicode(self.ui.langCombo.currentText())
        desc = 'Search subtitles for "%s" (lang:%s)' % (tosearch, lang)
        self.parent.doAction(desc, self.parent.searchSubtitleAction, [lang, tosearch])

    def searchTorrent(self):
        tosearch = self.movie.original_title
        if not empty(self.movie.release_date):
            tosearch += ' %s' % self.movie.release_date.year
        desc = 'Search torrents for "%s"' % tosearch
        self.parent.doAction(desc, self.parent.searchTorrentAction, [tosearch])

    def casting(self):
        role = None
        tosearch = unicode(self.ui.castingCombo.currentText())
        role_desc = ''
        if tosearch != 'all':
            role = tosearch
            role_desc = ' as %s' % role
        self.parent.doAction('Casting%s of movie "%s"' % (role_desc, self.movie.original_title),
                             self.parent.castingAction, [self.backend.name, self.movie.id, role])
