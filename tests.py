#!/usr/bin/env python
import unittest

from grabber import *


class TestUrlToFilepath(unittest.TestCase):
    def test_1(self):
        result = url_to_filepath('http://example.com')
        self.assertEqual(result, 'example.com/index.txt')

    def test_2(self):
        result = url_to_filepath('http://example.com/')
        self.assertEqual(result, 'example.com/index.txt')

    def test_3(self):
        result = url_to_filepath('http://example.com/news')
        self.assertEqual(result, 'example.com/news/index.txt')

    def test_4(self):
        result = url_to_filepath('http://example.com/news/')
        self.assertEqual(result, 'example.com/news/index.txt')

    def test_5(self):
        result = url_to_filepath('http://example.com/news/index.html')
        self.assertEqual(result, 'example.com/news/index.txt')


if __name__ == '__main__':
    unittest.main()
