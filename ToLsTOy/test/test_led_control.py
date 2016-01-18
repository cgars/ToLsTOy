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


class TestLedControll(unittest.TestCase):
    """
    Tests for the LEDTower model
    """
    def setUp(self):
        self.io_mock = mock.MagicMock()
        self.io_mock.intensity = 125
        self.io_mock.DO_WritePort.return_value = self.io_mock.DO_WritePort
        self.ctr = ToLsTOy.led_control.LEDTowers(io=self.io_mock)

    def test_init(self):
        """
        Test whether the io card initialisation call has been done in init
        """
        self.assertEqual(self.io_mock.method_calls[0][1], (9, 0))

    def test_write(self):
        """
        Test ensuring that proper values woudl be written to the io card
        :return:
        """
        sdi = self.ctr.__sdi__
        sdi_mock = mock.MagicMock()
        self.ctr.__sdi__ = sdi_mock
        self.ctr.write(ToLsTOy.led_control.LEDTowers.LDAC3_PORT,
                       ToLsTOy.led_control.LEDTowers.CS3_PORT,
                       125)
        self.assertListEqual([e[0] for e in sdi_mock.call_args_list],
                [('1',), ('1',), ('1',), ('1',), ('0',), ('1',), ('1',), ('1',), ('1',), ('1',), ('0',), ('1',)])
        sdi_mock.reset_mock()
        self.ctr.write(ToLsTOy.led_control.LEDTowers.LDAC3_PORT,
                       ToLsTOy.led_control.LEDTowers.CS3_PORT, 180)
        self.assertListEqual([e[0] for e in sdi_mock.call_args_list],
                [('1',), ('1',), ('1',), ('1',), ('1',), ('0',), ('1',), ('1',), ('0',), ('1',), ('0',), ('0',)])

        self.assertNotEqual([e[0] for e in sdi_mock.call_args_list],
                [('1',), ('1',), ('1',), ('1',), ('0',), ('1',), ('1',), ('1',), ('1',), ('1',), ('0',), ('1',)])
        self.ctr.__sdi__ = sdi

    def test_shock_event(self):
        """
        Test that shock events are correctly written to write
        """
        shock_mock = mock.MagicMock()
        shock_mock.intensity = 125
        write_mock = mock.MagicMock()
        self.ctr.write = write_mock
        self.ctr.send_shock_event(shock_mock)
        self.assertEqual(write_mock.call_args_list[0][0], (4, 7, 125))

    def test_light_event(self):
        """
        Test that color events are correctly written to write
        """
        light_mock = mock.MagicMock()
        write_mock = mock.MagicMock()
        self.ctr.write = write_mock
        light_mock.blue = [125, 125, 255, 128]
        light_mock.green = [1, 2, 3, 4]
        self.ctr.send_light_event(light_mock)
        x = [e[1][2] for e in write_mock.mock_calls]
        self.assertListEqual(x, [125, 125, 255, 128, 1, 2, 3, 4])

    def test_sdi(self):
        """
        Check for corerct write for sdi
        """
        write_mock = mock.MagicMock()
        self.ctr.write_to_port = write_mock
        self.ctr.__sdi__('1')
        self.assertListEqual(write_mock.call_args[0][0], ['0', '0', '0', '0', '0', '0', '0', '1'])

    def test_write_to_port(self):
        """
        Ttest for correct call of the DO_WritePort function
        """
        self.ctr.write_to_port(['0', '0', '0', '0', '0', '0', '0', '1'])
        self.assertEqual(self.io_mock.DO_WritePort.call_args_list[0][0][2], 1)
        self.ctr.write_to_port(['0', '0', '0', '0', '0', '0', '1', '0'])
        self.assertEqual(self.io_mock.DO_WritePort.call_args_list[1][0][2], 2)


if __name__ == '__main__':
    unittest.main()
