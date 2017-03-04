import unittest
import env

from memeServer import models


class TestModels(unittest.TestCase):

    def test_recents(self):
        recents = models.get_recents()
        self.assertTrue(True)