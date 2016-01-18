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
import time

import ToLsTOy
import ToLsTOy.gui
import ToLsTOy.led_control


class TestAll(unittest.TestCase):
    control = None
    io = None
    app = None
    root = None

    @classmethod
    def setUpClass(cls):
        io = mock.MagicMock()
        control = ToLsTOy.led_control.Control(ToLsTOy.led_control.LEDTowers(io))
        root = Tk()
        app = ToLsTOy.gui.MainFrame(root, control)
        TestAll.io = io
        TestAll.control = control
        TestAll.app = app
        TestAll.root = root

    @classmethod
    def tearDownClass(cls):
        TestAll.io = None
        TestAll.control = None
        TestAll.app = None
        TestAll.root = None

    def test_idle(self):
        """
        Valid values in the idle frames color etxts should result in
        a set of correct calls of the io cards DO_WWritePort function
        """
        app = TestAll.app
        app.idle_frame.blue.delete(1., END)
        app.idle_frame.blue.insert(END, '125,180,000,000')
        app.idle_frame.key_pressed(mock.MagicMock())
        io = TestAll.io
        write_calls = filter(lambda x: x[0] == 'DO_WritePort', io.method_calls)
        write_values = [e[1][2] for e in write_calls]
        self.assertEqual(sum(write_values), 66663)
        self.assertEqual(len(write_values), 320)
        io.reset_mock()

    def test_light(self):
        """
        Valid set of lines in the light table should lead to a correctly timed
        set of calls to the DO_WWritePort function of the io
        """
        app = TestAll.app
        table = app.color_table
        table.rows[-1].add_row()
        table.rows[-1].add_row()
        table.rows[-1].add_row()
        table.rows[-1].add_row()
        table.rows[0].texts[2].insert(END, '5')
        event = mock.MagicMock()
        event.widget = table.rows[0].texts[2]
        table.text_field_change(event)
        table.rows[0].texts[3].insert(END, '125,125,13,13')
        event = mock.MagicMock()
        event.widget = table.rows[0].texts[3]
        table.text_field_change(event)
        table.rows[0].texts[4].insert(END, '125,125,13,15')
        event = mock.MagicMock()
        event.widget = table.rows[0].texts[4]
        table.text_field_change(event)
        table.rows[1].texts[1].insert(END, '0,2')
        event = mock.MagicMock()
        event.widget = table.rows[1].texts[1]
        table.text_field_change(event)
        tick = time.time()
        app.thread_done = mock.MagicMock()
        app.start_all()
        while not app.thread_done.called:
            pass
        tock = time.time()
        print tock - tick
        self.assertLess(tock - tick - 15, 2)
        io = TestAll.io
        write_calls = filter(lambda x: x[0] == 'DO_WritePort', io.method_calls)
        write_values = [e[1][2] for e in write_calls]
        self.assertEqual(sum(write_values), 287182)
        self.assertEqual(len(write_values), 1360)

if __name__ == '__main__':
    unittest.main()