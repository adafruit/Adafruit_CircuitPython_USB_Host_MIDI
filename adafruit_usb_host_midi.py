# SPDX-FileCopyrightText: Copyright (c) 2023 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_usb_host_midi`
================================================================================

CircuitPython USB host driver for MIDI devices


* Author(s): Scott Shawcroft
"""

import adafruit_usb_host_descriptors

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_MIDI.git"


DIR_IN = 0x80

class MIDI:
    def __init__(self, device):
        self.interface_number = 0
        self.in_ep = 0
        self.out_ep = 0
        self.device = device

        self.buf = bytearray(64)
        self.start = 0
        self._remaining = 0

        config_descriptor = adafruit_usb_host_descriptors.get_configuration_descriptor(
            device, 0
        )

        i = 0
        midi_interface = False
        while i < len(config_descriptor):
            descriptor_len = config_descriptor[i]
            descriptor_type = config_descriptor[i + 1]
            if descriptor_type == adafruit_usb_host_descriptors.DESC_CONFIGURATION:
                config_value = config_descriptor[i + 5]
            elif descriptor_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
                interface_number = config_descriptor[i + 2]
                interface_class = config_descriptor[i + 5]
                interface_subclass = config_descriptor[i + 6]
                midi_interface = interface_class == 0x1 and interface_subclass == 0x3
                if midi_interface:
                    self.interface_number= interface_number

            elif descriptor_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
                endpoint_address = config_descriptor[i + 2]
                if endpoint_address & DIR_IN:
                    if midi_interface:
                        self.in_ep = endpoint_address
                else:
                    if midi_interface:
                        self.out_ep = endpoint_address
            i += descriptor_len

        device.set_configuration()
        device.detach_kernel_driver(self.interface_number)

    def read(self, size):
        if self._remaining == 0:
            self._remaining = self.device.read(self.in_ep, self.buf) - 1
            self.start = 1
        size = min(size, self._remaining)
        b = self.buf[self.start:self.start + size]
        self.start += size
        self._remaining -= size
        return b

    def readinto(self, buf):
        b = self.read(len(buf))
        n = len(b)
        if n:
            buf[:] = b
        return n

    def __repr__(self):
        # also idProduct/idVendor for vid/pid
        return "MIDI Device " + str(self.device.manufacturer) + "/" + str(self.device.product)
