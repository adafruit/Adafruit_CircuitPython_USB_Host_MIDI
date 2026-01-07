# SPDX-FileCopyrightText: Copyright (c) 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import adafruit_midi
import adafruit_tlv320
import audiobusio
import board
import synthio
import usb.core
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from displayio import release_displays
from pwmio import PWMOut

import adafruit_usb_host_midi

release_displays()
print("Looking for midi device")
raw_midi = None
while raw_midi is None:
    for device in usb.core.find(find_all=True):
        try:
            raw_midi = adafruit_usb_host_midi.MIDI(device, timeout=0.01)
            print("Found", hex(device.idVendor), hex(device.idProduct))
        except ValueError:
            continue


mclk_pwm = PWMOut(board.I2S_MCLK, frequency=15_000_000, duty_cycle=2**15)

i2c = board.I2C()
dac = adafruit_tlv320.TLV320DAC3100(i2c)

# set sample rate & bit depth, use bclk
dac.configure_clocks(sample_rate=44100, bit_depth=16, mclk_freq=15_000_000)

# use headphones
dac.headphone_output = True
dac.dac_volume = -5  # dB
dac.headphone_volume = -30
audio = audiobusio.I2SOut(board.I2S_BCLK, board.I2S_WS, board.I2S_DIN)

synth = synthio.Synthesizer(sample_rate=44100)
audio.play(synth)

midi = adafruit_midi.MIDI(midi_in=raw_midi, in_channel=0)

pressed = {}

while True:
    msg = midi.receive()
    if isinstance(msg, NoteOn) and msg.velocity != 0:
        note = synthio.Note(synthio.midi_to_hz(msg.note))
        print("noteOn: ", msg.note, "vel:", msg.velocity)
        synth.press(note)
        pressed[msg.note] = note
    elif (
        isinstance(msg, NoteOff) or (isinstance(msg, NoteOn) and msg.velocity == 0)
    ) and msg.note in pressed:
        print("noteOff:", msg.note, "vel:", msg.velocity)
        note = pressed[msg.note]
        synth.release(note)
        del pressed[msg.note]
