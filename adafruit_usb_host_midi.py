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
import usb.core

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_MIDI.git"


DIR_IN = 0x80

# MIDI bytes per USB packet, indexed by code index number. USB MIDI 1.0, table 4-1.
_CIN_LENGTH = (0, 0, 2, 3, 3, 1, 2, 3, 3, 3, 3, 3, 2, 2, 3, 1)


class MIDI:
    """
    Stream-like MIDI device for use with ``adafruit_midi`` and similar upstream
    MIDI parser libraries.

    :param device: a ``usb.core.Device`` object which implements
        ``read(endpoint, buffer)`` and ``write(endpoint,buffer)``
    :param float timeout: timeout in seconds to wait for read or write operation
        to succeed. Default to 0.01. None blocks until data arrives, which can
        leave messages from a multi-packet transfer waiting in the parser's buffer.
    """

    def __init__(self, device, timeout=0.01):
        self.interface_number = 0
        self.in_ep = 0
        self.out_ep = 0
        self.device = device
        self.timeout_ms = round(timeout * 1000) if timeout else 0

        in_ep_max_packet_size = 0
        self.start = 0
        self._remaining = 0

        config_descriptor = adafruit_usb_host_descriptors.get_configuration_descriptor(device, 0)

        i = 0
        midi_interface = False
        while i < len(config_descriptor):
            descriptor_len = config_descriptor[i]
            descriptor_type = config_descriptor[i + 1]
            if descriptor_type == adafruit_usb_host_descriptors.DESC_CONFIGURATION:
                # pylint: disable=unused-variable
                config_value = config_descriptor[i + 5]  # noqa: F841
                # pylint: enable=unused-variable
            elif descriptor_type == adafruit_usb_host_descriptors.DESC_INTERFACE:
                interface_number = config_descriptor[i + 2]
                interface_class = config_descriptor[i + 5]
                interface_subclass = config_descriptor[i + 6]
                midi_interface = interface_class == 0x1 and interface_subclass == 0x3
                if midi_interface:
                    self.interface_number = interface_number

            elif descriptor_type == adafruit_usb_host_descriptors.DESC_ENDPOINT:
                endpoint_address = config_descriptor[i + 2]
                if endpoint_address & DIR_IN:
                    if midi_interface:
                        self.in_ep = endpoint_address
                        in_ep_max_packet_size = config_descriptor[i + 4] | (
                            config_descriptor[i + 5] << 8
                        )
                elif midi_interface:
                    self.out_ep = endpoint_address
            i += descriptor_len

        # A read never returns more than one packet unless it fills the buffer, so a
        # buffer bigger than the endpoint's packet size waits for packets that may
        # never come and times out instead. Some devices use 4 byte packets.
        self.buf = bytearray(in_ep_max_packet_size or 64)
        self._decoded = bytearray(len(self.buf))

        device.set_configuration()
        device.detach_kernel_driver(self.interface_number)

    def read(self, size):
        """
        Read bytes.  If ``nbytes`` is specified then read at most that many
        bytes. Otherwise, read everything that arrives until the connection
        times out. Providing the number of bytes expected is highly recommended
        because it will be faster. If no bytes are read, return ``None``.

        .. note:: When no bytes are read due to a timeout, this function returns ``None``.
          This matches the behavior of `io.RawIOBase.read` in Python 3, but
          differs from pyserial which returns ``b''`` in that situation.

        :return: Data read
        :rtype: bytes or None
        """

        if self._remaining == 0:
            try:
                n = self.device.read(self.in_ep, self.buf, self.timeout_ms)
                self._decode(n)
            except usb.core.USBTimeoutError:
                pass
        size = min(size, self._remaining)
        b = self._decoded[self.start : self.start + size]
        self.start += size
        self._remaining -= size
        return b

    def _decode(self, n):
        """Unpack the MIDI bytes from the 4 byte USB packets in ``self.buf``."""
        count = 0
        for i in range(0, n - 3, 4):
            # The low nibble of the first byte is the code index number. It gives the
            # length of the message, so the rest of the packet is padding and dropping
            # it keeps the header bytes of later packets out of the MIDI stream.
            for j in range(1, _CIN_LENGTH[self.buf[i] & 0xF] + 1):
                self._decoded[count] = self.buf[i + j]
                count += 1
        self.start = 0
        self._remaining = count

    def readinto(self, buf):
        """Read bytes into the ``buf``. Read at most ``len(buf)`` bytes.

        :return: number of bytes read and stored into ``buf``
        :rtype: int or None (on a non-blocking error)
        """
        b = self.read(len(buf))
        n = len(b)
        if n:
            buf[:] = b
        return n

    def __repr__(self):
        # also idProduct/idVendor for vid/pid
        return "MIDI Device " + str(self.device.manufacturer) + "/" + str(self.device.product)
