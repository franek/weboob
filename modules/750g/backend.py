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

from weboob.capabilities.recipe import ICapRecipe, Recipe
from weboob.tools.backend import BaseBackend

from .browser import SevenFiftyGramsBrowser

__all__ = ['SevenFiftyGramsBackend']


class SevenFiftyGramsBackend(BaseBackend, ICapRecipe):
    NAME = '750g'
    MAINTAINER = u'Julien Veyssier'
    EMAIL = 'julien.veyssier@aiur.fr'
    VERSION = '0.f'
    DESCRIPTION = '750g recipe website'
    LICENSE = 'AGPLv3+'
    BROWSER = SevenFiftyGramsBrowser

    def create_default_browser(self):
        return self.create_browser()

    def get_recipe(self, id):
        return self.browser.get_recipe(id)

    def iter_recipes(self, pattern):
        return self.browser.iter_recipes(pattern.encode('utf-8'))

    def fill_recipe(self, recipe, fields):
        if 'nb_person' in fields or 'instructions' in fields:
            rec = self.get_recipe(recipe.id)
            recipe.picture_url = rec.picture_url
            recipe.instructions = rec.instructions
            recipe.ingredients = rec.ingredients
            recipe.comments = rec.comments
            recipe.author = rec.author
            recipe.nb_person = rec.nb_person
            recipe.cooking_time = rec.cooking_time
            recipe.preparation_time = rec.preparation_time

        return recipe

    OBJECTS = {
        Recipe: fill_recipe,
    }
