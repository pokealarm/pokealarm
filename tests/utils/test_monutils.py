# -*- coding: utf-8 -*-

# Standard Library Imports
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
