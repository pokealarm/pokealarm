# -*- coding: utf-8 -*-

# Standard Library Imports
from __future__ import absolute_import, unicode_literals
import unittest
# 3rd Party Imports
# Local Imports
from prototype.utils import monutils


class TestMonUtils(unittest.TestCase):

    def test_get_atk_stat(self):
        atk_stat = monutils.get_atk_stat(1)
        self.assertTrue(type(atk_stat) == int)
        self.assertTrue(atk_stat == 118)

    def test_get_def_stat(self):
        def_stat = monutils.get_def_stat(2)
        self.assertTrue(type(def_stat) == int)
        self.assertTrue(def_stat == 151)

    def test_get_sta_stat(self):
        def_stat = monutils.get_def_stat(3)
        self.assertTrue(type(def_stat) == int)
        self.assertTrue(def_stat == 198)

    def test_get_types(self):
        types = monutils.get_types(1)
        self.assertTrue(type(types) == tuple)
        self.assertTrue(types == (12, 4))
        types = monutils.get_types(4)
        self.assertTrue(type(types) == tuple)
        self.assertTrue(types == (10,))

    def test_is_legendary(self):
        legendary = monutils.is_legendary(1)
        self.assertTrue(type(legendary) == bool)
        self.assertTrue(not legendary)
        legendary = monutils.is_legendary(150)
        self.assertTrue(type(legendary) == bool)
        self.assertTrue(legendary)

    def test_get_generation(self):
        gen = monutils.get_generation(1)
        self.assertTrue(type(gen) == int)
        self.assertTrue(gen == 1)

    def test_get_height(self):
        height = monutils.get_height(4)
        self.assertTrue(type(height) == float)
        self.assertTrue(height == 0.61)

    def test_get_weight(self):
        weight = monutils.get_weight(4)
        self.assertTrue(type(weight) == float)
        self.assertTrue(weight == 8.5)

    def test_get_move_type(self):
        move_type = monutils.get_move_type(13)
        self.assertTrue(type(move_type) == int)
        self.assertTrue(move_type == 1)

    def test_get_move_damage(self):
        dmg = monutils.get_move_damage(14)
        self.assertTrue(type(dmg) == int)
        self.assertTrue(dmg == 150)

    def test_get_move_dps(self):
        dps = monutils.get_move_dps(16)
        self.assertTrue(type(dps) == float)
        self.assertTrue(dps == 26.67)

    def test_get_move_duration(self):
        duration = monutils.get_move_duration(18)
        self.assertTrue(type(duration) == int)
        self.assertTrue(duration == 2100)

    def test_get_move_energy(self):
        energy = monutils.get_move_energy(20)
        self.assertTrue(type(energy) == int)
        self.assertTrue(energy == 33)

    def test_get_weather_boosted_types(self):
        types = monutils.get_weather_boosted_types(1)
        self.assertTrue(type(types) == list)
        self.assertTrue(types == [10, 12, 5])

    def test_get_cp_multiplier(self):
        multiplier = monutils.get_cp_multiplier(10)
        self.assertTrue(type(multiplier) == float)
        self.assertTrue(multiplier == 0.422500014305115)
