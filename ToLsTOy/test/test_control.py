# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
#
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------


import unittest
import mock

import ToLsTOy.led_control


class TestControll(unittest.TestCase):
    """
    Tests for the Controll Class
    """
    def setUp(self):
        """
        Creates mocks for the gui and the hardware and initiates teh Controll object
        """
        self.gui_mock = mock.MagicMock()
        self.hardware_mock = mock.MagicMock()
        self.ctr = ToLsTOy.led_control.Control(self.hardware_mock)

    def tearDown(self):
        self.ctr.run = mock.MagicMock()
        self.ctr.start()

    def test_send_event(self):
        """
        Tests whether the send event method correctly discriminates between Shock and Color events
        Should assert for unknown type
        """
        self.ctr.send_event(mock.MagicMock(spec=ToLsTOy.led_control.ShockEvent))
        self.assertEqual(self.hardware_mock.send_shock_event.call_count, 1)
        self.ctr.send_event(mock.MagicMock(spec=ToLsTOy.led_control.ColorEvent))
        self.assertEqual(self.hardware_mock.send_shock_event.call_count, 1)
        self.assertEqual(self.hardware_mock.send_light_event.call_count, 1)
        with self.assertRaises(AssertionError):
            self.ctr.send_event(mock.MagicMock())

    def test_calculate_timepoints(self):
        """
        Test whether timpoints are correctly calculated
        """
        event_list_mock = mock.MagicMock()
        event_list_mock.duration = 10
        event_list_mock.__iter__.return_value = [event_list_mock, event_list_mock, event_list_mock]
        event_list = self.ctr.calculate_timepoints(event_list_mock)
        self.assertEqual(event_list_mock.start, 20)

    def test_get_shock_event_list(self):
        """
        Test whether Shock events are correctly created given
        a certain shock protocol
        """
        shock_protocoll = [[False, 4.0, 20, False],
                           [False, 10.0, 30, False],
                           [[0, 2], False, False, False],
                           [False, 1, 0]]
        shock_event_list = self.ctr.get_shock_event_list(shock_protocoll)
        self.assertEqual(shock_event_list[0].duration, 4)
        self.assertEqual(shock_event_list[0].intensity, 20)
        self.assertEqual(shock_event_list[1].duration, 10)
        self.assertEqual(shock_event_list[1].intensity, 30)
        self.assertEqual(shock_event_list[2].duration, 4)
        self.assertEqual(shock_event_list[2].intensity, 20)
        self.assertEqual(len(shock_event_list), 7)

    def test_get_color_event_list(self):
        """
        Test whether Color events are correctly created given
        a certain  protocol
        """
        c_protocoll = [
            [False, False, False, False, False],
            [False, 25.0, [1, 1, 1, 1], [2, 2, 2, 2], False],
            [False, 1, [0, 0, 0, 0], [0, 0, 0, 0]],
            [[0, 2], False, False, False, False]
        ]
        color_event_list = self.ctr.get_color_event_list(c_protocoll)
        self.assertEqual(color_event_list[0].green, [2, 2, 2, 2])
        self.assertEqual(color_event_list[0].blue, [1, 1, 1, 1])
        self.assertEqual(color_event_list[0].duration, 25)
        self.assertEqual(color_event_list[1].green, [0, 0, 0, 0])
        self.assertEqual(color_event_list[1].blue, [0, 0, 0, 0])
        self.assertEqual(color_event_list[1].duration, 1)
        self.assertEqual(len(color_event_list), 6)


if __name__ == '__main__':
    unittest.main()
