Introduction
============


.. image:: https://readthedocs.org/projects/adafruit-circuitpython-usb-host-midi/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/usb-host-midi/en/latest/
    :alt: Documentation Status


.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_MIDI/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_MIDI/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython USB host driver for MIDI devices


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-usb-host-midi/>`_.
To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-usb-host-midi

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-usb-host-midi

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install adafruit-circuitpython-usb-host-midi

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install adafruit_usb_host_midi

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python

  import adafruit_midi
  import adafruit_usb_host_midi

  print("Looking for midi device")
  raw_midi = None
  while raw_midi is None:
      for device in usb.core.find(find_all=True):
          try:
              raw_midi = adafruit_usb_host_midi.MIDI(device)
              print("Found", hex(device.idVendor), hex(device.idProduct))
          except ValueError:
              continue

  midi_device = adafruit_midi.MIDI(midi_in=raw_midi, in_channel=0)


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/usb-host-midi/en/latest/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_USB_Host_MIDI/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
