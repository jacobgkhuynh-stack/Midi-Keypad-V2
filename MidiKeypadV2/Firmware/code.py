import keypad
import touchio
from microcontroller import pin

from kmk.extensions.media_keys import MediaKeys
from kmk.modules.tapdance import TapDance
from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.encoder import EncoderHandler
from kmk.modules.midi import MidiKeys
from kmk.scanners import Scanner
from kmk.scanners.keypad import KeysScanner


# KMK doesn't have a scanner for touch pads, so here's a tiny one.
# Don't touch the pads while the board boots - they calibrate on startup!
class TouchScanner(Scanner):
    def __init__(self, pins):
        self.pads = [touchio.TouchIn(p) for p in pins]
        self.pressed = [False] * len(pins)

    @property
    def key_count(self):
        return len(self.pads)

    def scan_for_changes(self):
        for i, pad in enumerate(self.pads):
            touched = pad.value
            if touched != self.pressed[i]:
                self.pressed[i] = touched
                return keypad.Event(i + self.offset, touched)


keyboard = KMKKeyboard()
# These have to be created before we use KC.MIDI_NOTE / KC.VOLU below
tap_dance = TapDance()
midi = MidiKeys()
media_keys = MediaKeys()

MEDIA_CTRL = KC.TD(
    KC.MPLY,  # 1 Click: Play / Pause
    KC.MNXT,  # 2 Clicks: Next Track (Forward)
    KC.MPRV,  # 3 Clicks: Previous Track (Back)
)

keyboard.matrix = [
    TouchScanner([pin.GPIO7, pin.GPIO8, pin.GPIO9, pin.GPIO10, pin.GPIO11, pin.GPIO12, pin.GPIO13]),
]

# Touch pads play a C major scale.
keyboard.keymap = [[
    KC.MIDI_NOTE(60), KC.MIDI_NOTE(62), KC.MIDI_NOTE(64), KC.MIDI_NOTE(65),
    KC.MIDI_NOTE(67), KC.MIDI_NOTE(69), KC.MIDI_NOTE(71)
]]

# Rotary encoder controls your computer's volume, brightness and media.
encoder = EncoderHandler()
encoder.pins = (
    (pin.GPIO6, pin.GPIO5, pin.GPIO4),   # Encoder 1
    (pin.GPIO3, pin.GPIO2, pin.GPIO44), # Encoder 2
    (pin.GPIO1, pin.GPIO43, None) # Encoder 3 Third pin is GPIO44
)
keyboard.extensions = [media_keys]
encoder.map = [
    (
        (KC.VOLD, KC.VOLU, MEDIA_CTRL),  # Encoder 1: Volume down / up
        (KC.BRID, KC.BRIU, KC.NO),  # Encoder 2: Brightness down / up (example)
        (KC.LEFT, KC.RIGHT, KC.NO), # Encoder 3: Left / Right arrows
    )
]

keyboard.modules = [midi, encoder, tap_dance]

if __name__ == '__main__':
    keyboard.go()
