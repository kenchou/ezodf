#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: test node organizer
# Created: 31.01.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import unittest

# test helpers
from mytesttools import create_node

# objects to test
from ezodf.nodeorganizer import PreludeTagBlock

class CounterFacade:
    def __init__(self, tags):
        self.tags = tags

    def count(self, xmlnode):
        prelude = PreludeTagBlock(xmlnode, self.tags)
        return len(prelude)

class TestCounter(unittest.TestCase):
    def test_aabbcc(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('aabbccddeeff'))
        self.assertEqual(counter.count(node), 6)

    def test_bbcc(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('bbccddeeff'))
        self.assertEqual(counter.count(node), 4)

    def test_cc(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('ccddeeff'))
        self.assertEqual(counter.count(node), 2)

    def test_only_aa(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('aa'))
        self.assertEqual(counter.count(node), 2)

    def test_only_bb(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('bb'))
        self.assertEqual(counter.count(node), 2)

    def test_only_cc(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('cc'))
        self.assertEqual(counter.count(node), 2)

    def test_no_tags(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list(''))
        self.assertEqual(counter.count(node), 0)

    def test_no_matches(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('ddeeff'))
        self.assertEqual(counter.count(node), 0)

    def test_invalid_prelude(self):
        counter = CounterFacade(list('abc'))
        node = create_node(list('dadeeff'))
        self.assertEqual(counter.count(node), 0)


class TestPreludeTagBlockBasics(unittest.TestCase):
    def test_xmlnode_is_none_error(self):
        with self.assertRaises(ValueError):
            PreludeTagBlock(None, '')

    def test_no_prelude_tags(self):
        with self.assertRaises(ValueError):
            PreludeTagBlock(create_node('abc'), '')

    def test_unique_order_tags(self):
        with self.assertRaises(ValueError):
            PreludeTagBlock(create_node('abc'), 'abcc')

    def test_all_tags_exist(self):
        tree = create_node('aabbccghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 6)

    def test_only_aa(self):
        tree = create_node('aaghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 2)

    def test_only_bb(self):
        tree = create_node('bbghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 2)

    def test_only_cc(self):
        tree = create_node('ccghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 2)

    def test_prelude_only_tree(self):
        tree = create_node('aabbcc')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 6)

    def test_without_prelude(self):
        tree = create_node('ghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 0)

    def test_empty_tree(self):
        tree = create_node('')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 0)

    def test_from_not_well_formed_tree(self):
        tree = create_node('haabbccghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        self.assertEqual(len(ptb), 0)

class TestPreludeTagBlockInfo(unittest.TestCase):
    def test_tag_info_a(self):
        tree = create_node('aabbccghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        start_index, count = ptb.tag_info('a')
        self.assertEqual((0, 2), (start_index, count))

    def test_tag_info_b(self):
        tree = create_node('aabbbccghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        start_index, count = ptb.tag_info('b')
        self.assertEqual((2, 3), (start_index, count))

    def test_tag_info_for_not_existing_tag(self):
        tree = create_node('aabbbghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        start_index, count = ptb.tag_info('c')
        self.assertEqual((-1, 0), (start_index, count))

    def test_tag_info_invalid_tag_error(self):
        tree = create_node('aabbbghixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        with self.assertRaises(ValueError):
            ptb.tag_info('d')

    def test_tag_info_tag_not_in_prelude_block(self):
        tree = create_node('aabbbgccixyz')
        ptb = PreludeTagBlock(tree, 'abc')
        start_index, count = ptb.tag_info('c')
        self.assertEqual((-1, 0), (start_index, count))

class TestPreludeTagBlockInsertPositionBefore(unittest.TestCase):
    def test_tag_error(self):
        tree = create_node('aabbccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')
        with self.assertRaises(ValueError):
            tb.insert_position_before('d')

    def test_before_existing_tag(self):
        tree = create_node('aabbccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_before('a'), 0)
        self.assertEqual(tb.insert_position_before('b'), 2)
        self.assertEqual(tb.insert_position_before('c'), 4)

    def test_before_not_existing_tag(self):
        tree = create_node('aaccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_before('a'), 0)
        self.assertEqual(tb.insert_position_before('b'), 2)
        self.assertEqual(tb.insert_position_before('c'), 2)

    def test_without_prelude(self):
        tree = create_node('ghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_before('a'), 0)
        self.assertEqual(tb.insert_position_before('b'), 0)
        self.assertEqual(tb.insert_position_before('c'), 0)

    def test_for_empty_node(self):
        tree = create_node('')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_before('a'), 0)
        self.assertEqual(tb.insert_position_before('b'), 0)
        self.assertEqual(tb.insert_position_before('c'), 0)

class TestPreludeTagBlockInsertPositionAfter(unittest.TestCase):
    def test_tag_error(self):
        tree = create_node('aabbccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')
        with self.assertRaises(ValueError):
            tb.insert_position_after('d')

    def test_after_existing_tag(self):
        tree = create_node('aabbccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_after('a'), 2)
        self.assertEqual(tb.insert_position_after('b'), 4)
        self.assertEqual(tb.insert_position_after('c'), 6)

    def test_after_not_existing_tag(self):
        tree = create_node('aaccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_after('a'), 2)
        self.assertEqual(tb.insert_position_after('b'), 2)
        self.assertEqual(tb.insert_position_after('c'), 4)

    def test_without_prelude(self):
        tree = create_node('ghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_after('a'), 0)
        self.assertEqual(tb.insert_position_after('b'), 0)
        self.assertEqual(tb.insert_position_after('c'), 0)

    def test_for_empty_node(self):
        tree = create_node('')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_after('a'), 0)
        self.assertEqual(tb.insert_position_after('b'), 0)
        self.assertEqual(tb.insert_position_after('c'), 0)

    def test_after_all_prelude_tags(self):
        tree = create_node('aabbccghixxyyzz')
        tb = PreludeTagBlock(tree, 'abc')

        self.assertEqual(tb.insert_position_after(), 6)

if __name__=='__main__':
    unittest.main()