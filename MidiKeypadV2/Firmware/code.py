import keypad
import touchio
from microcontroller import pin

from kmk.extensions.media_keys import MediaKeys
from kmk.keys import KC
from kmk.kmk_keyboard import KMKKeyboard
from kmk.modules.encoder import EncoderHandler
from kmk.modules.midi import MidiKeys
from kmk.modules.tapdance import TapDance
from kmk.scanners import Scanner


# Custom scanner for capacitive touch pads.
# Don't touch the pads while the board boots - they calibrate on startup!
class TouchScanner(Scanner):
    def __init__(self, pins):
        super().__init__()
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
        return None


keyboard = KMKKeyboard()

# Initialize modules/extensions before referencing their keycodes (KC.TD, KC.MIDI_NOTE, KC.VOLU)
tap_dance = TapDance()
midi = MidiKeys()
media_keys = MediaKeys()
encoder = EncoderHandler()

MEDIA_CTRL = KC.TD(
    KC.MPLY,  # 1 Click: Play / Pause
    KC.MNXT,  # 2 Clicks: Next Track (Forward)
    KC.MPRV,  # 3 Clicks: Previous Track (Back)
)

keyboard.matrix = [
    TouchScanner([
        pin.GPIO7,
        pin.GPIO8,
        pin.GPIO9,
        pin.GPIO10,
        pin.GPIO11,
        pin.GPIO12,
        pin.GPIO13,
    ]),
]

# Touch pads play a C major scale (C4 to B4).
keyboard.keymap = [[
    KC.MIDI_NOTE(60),
    KC.MIDI_NOTE(62),
    KC.MIDI_NOTE(64),
    KC.MIDI_NOTE(65),
    KC.MIDI_NOTE(67),
    KC.MIDI_NOTE(69),
    KC.MIDI_NOTE(71),
]]

# Rotary encoders: (Pin A, Pin B, Button Pin)
# Encoders 2 & 3 share GPIO44 physically; keep Encoder 3's button as None to avoid pin conflict.
encoder.pins = (
    (pin.GPIO6, pin.GPIO5, pin.GPIO4),   # Encoder 1
    (pin.GPIO3, pin.GPIO2, pin.GPIO44),  # Encoder 2 (shared button line on GPIO44)
    (pin.GPIO1, pin.GPIO43, None),       # Encoder 3 (button wired in parallel to GPIO44)
)

encoder.map = [
    (
        (KC.VOLD, KC.VOLU, MEDIA_CTRL),  # Encoder 1: Volume down / up / Media TapDance
        (KC.BRID, KC.BRIU, KC.NO),       # Encoder 2: Brightness down / up / Shared button
        (KC.LEFT, KC.RIGHT, KC.NO),      # Encoder 3: Left / Right arrows
    )
]

keyboard.extensions = [media_keys]
keyboard.modules = [midi, encoder, tap_dance]

if __name__ == '__main__':
    keyboard.go()
