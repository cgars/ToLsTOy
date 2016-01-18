# -------------------------------------------------------------------------------
# Copyright (c) 2016 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
#
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------

import unittest
import mock
from Tkinter import *

import ToLsTOy.gui


class TestMainFrame(unittest.TestCase):
    """
    Tests for the Main frame
    """
    main_frame = None
    @classmethod
    def setUpClass(cls):
        root = Tk()
        TestMainFrame.main_frame = ToLsTOy.gui.MainFrame(root, control=mock.MagicMock())

    @classmethod
    def tearDownClass(cls):
        root = None
        TestMainFrame.main_frame = None

    def test_start(self):
        """
        Start all should call set values_and_start. the background should become red and the start button becomes
        a stop button
        """
        TestMainFrame.main_frame.start_all()
        self.assertEqual(TestMainFrame.main_frame.control.method_calls[0][0], 'set_values_and_start')
        self.assertEqual(TestMainFrame.main_frame.cget('bg'), 'red')
        self.assertEqual(TestMainFrame.main_frame.start_all_button.cget('text'), 'Stop')
        self.assertIn('stop', TestMainFrame.main_frame.start_all_button.cget('command'))

    def test_stop(self):
        """
        Stop should set the controls stop field to true
        :return:
        """
        TestMainFrame.main_frame.stop()
        self.assertTrue(TestMainFrame.main_frame.control.stop)

    def test_thread_done(self):
        """
        When thread_done is called background should go back to grey
        and the "start" button becomes a start button
        :return:
        """
        TestMainFrame.main_frame.thread_done()
        self.assertEqual(TestMainFrame.main_frame.cget('bg'), 'grey')
        self.assertEqual(TestMainFrame.main_frame.start_all_button.cget('text'), 'Start')
        self.assertIn('start_all', TestMainFrame.main_frame.start_all_button.cget('command'))


class TestIdleFrame(unittest.TestCase):
    """
    Tests for the idle frame
    """
    idle_frame = None

    @classmethod
    def setUpClass(cls):
        root = Tk()
        root.control = mock.MagicMock()
        TestIdleFrame.idle_frame = ToLsTOy.gui.IdleFrame(root)

    @classmethod
    def tearDownClass(cls):
        # root=None
        TestIdleFrame.idle_frame = None

    def test_get_colors(self):
        """
        Should return the values set in the text field id they are valid (bg green).
        Return False if there are no colors or if they are invalid (bg red)
        """
        self.assertEqual(TestIdleFrame.idle_frame.get_colors()[0], [0, 0, 0, 0])
        TestIdleFrame.idle_frame.blue.delete(1.0, END)
        TestIdleFrame.idle_frame.blue.insert(END, '125,000,000,180')
        self.assertEqual(TestIdleFrame.idle_frame.get_colors()[0], [125, 0, 0, 180])
        TestIdleFrame.idle_frame.blue.insert(END, '125,000,000,180')
        self.assertFalse(TestIdleFrame.idle_frame.get_colors())
        self.assertEqual(TestIdleFrame.idle_frame.cget('bg'), 'red')

    def test_key_pressed(self):
        """
        The idle_event of the control shoud ce called if the values are valid
        otherwise not
        """
        TestIdleFrame.idle_frame.blue.delete(1.0, END)
        TestIdleFrame.idle_frame.blue.insert(END, '125,000,000,180')
        TestIdleFrame.idle_frame.key_pressed(mock.MagicMock())
        self.assertEqual(TestIdleFrame.idle_frame.parent.control.method_calls[0][0], 'idle_event')
        self.assertEqual(TestIdleFrame.idle_frame.parent.control.method_calls[0][1],
                         (([125, 0, 0, 180], [0, 0, 0, 0]),))
        TestIdleFrame.idle_frame.blue.insert(END, 'asdasdsadasdasd')
        TestIdleFrame.idle_frame.key_pressed(mock.MagicMock())
        self.assertEqual(TestIdleFrame.idle_frame.parent.control.method_calls[0][0], 'idle_event')
        self.assertEqual(TestIdleFrame.idle_frame.parent.control.method_calls[0][1],
                         (([125, 0, 0, 180], [0, 0, 0, 0]),))


class TestLightTable(unittest.TestCase):
    light_table = None

    @classmethod
    def setUpClass(cls):
        root = Tk()
        TestLightTable.light_table = ToLsTOy.gui.LightTable(root)

    @classmethod
    def tearDownClass(cls):
        # root=None
        TestLightTable.light_table = None

    def test_get_all(self):
        """
        If valid values are set they should be returned
        """
        TestLightTable.light_table.rows[0].texts[4].insert(END, '1,1,1,1')
        event = mock.MagicMock()
        event.widget = TestLightTable.light_table.rows[0].texts[4]
        TestLightTable.light_table.text_field_change(event)
        self.assertEqual(TestLightTable.light_table.get_all_values()[0][3], [1, 1, 1, 1])

    def test_text_field_change(self):
        """
        Text fields bg should be green red or white dependent on whether there are valid color values
        invalid color value or no values
        """
        event = mock.MagicMock()
        self.assertEqual(TestLightTable.light_table.rows[0].texts[4].cget('bg'), 'green')
        TestLightTable.light_table.rows[0].texts[3].insert(END, '1,1')
        event.widget = TestLightTable.light_table.rows[0].texts[3]
        TestLightTable.light_table.text_field_change(event)
        self.assertEqual(TestLightTable.light_table.rows[0].texts[3].cget('bg'), 'red')
        TestLightTable.light_table.rows[0].texts[3].delete(1., END)
        TestLightTable.light_table.text_field_change(event)
        self.assertEqual(TestLightTable.light_table.rows[0].texts[3].cget('bg'), 'white')

class TestShockTable(unittest.TestCase):
    shock_table = None

    @classmethod
    def setUpClass(cls):
        root = Tk()
        TestShockTable.shock_table = ToLsTOy.gui.ShockTable(root)

    @classmethod
    def tearDownClass(cls):
        # root=None
        TestShockTable.shock_table = None

    def test_get_all(self):
        """
        If valid values are set they should be returned
        """
        TestShockTable.shock_table.rows[0].texts[3].insert(END, '10')
        event = mock.MagicMock()
        event.widget = TestShockTable.shock_table.rows[0].texts[3]
        TestShockTable.shock_table.text_field_change(event)
        self.assertEqual(TestShockTable.shock_table.get_all_values()[0][2], 10)

    def test_text_field_change(self):
        """
        Text fields bg should be green red or white dependent on whether there are valid values
        invalid values or no values
        """
        event = mock.MagicMock()
        self.assertEqual(TestShockTable.shock_table.rows[0].texts[3].cget('bg'), 'green')
        TestShockTable.shock_table.rows[0].texts[2].insert(END, 'asddas')
        event.widget = TestShockTable.shock_table.rows[0].texts[2]
        TestShockTable.shock_table.text_field_change(event)
        self.assertEqual(TestShockTable.shock_table.rows[0].texts[2].cget('bg'), 'red')
        TestShockTable.shock_table.rows[0].texts[2].delete(1., END)
        TestShockTable.shock_table.text_field_change(event)
        self.assertEqual(TestShockTable.shock_table.rows[0].texts[2].cget('bg'), 'white')
