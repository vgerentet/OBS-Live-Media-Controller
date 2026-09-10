"""
OBS communication module.

This module centralizes every communication with OBS Studio.
"""

import obsws_python as obs

from pynput import keyboard


# ==========================================================================
# Connection settings
# ==========================================================================

HOST = "localhost"
PORT = 4455
PASSWORD = "FGABFEDECDEAGFGDE##"


# ==========================================================================
# Global hotkey settings
# ==========================================================================

GLOBAL_HOTKEY = "*"


# ==========================================================================
# Keyboard helpers
# ==========================================================================

ALT_KEYS = {
    keyboard.Key.alt,
    keyboard.Key.alt_l,
    keyboard.Key.alt_r,
}


def parse_hotkey(hotkey_string):
    """
    Parse a hotkey string such as "<alt>+1" into modifiers and a key.

    Returns
    -------
    tuple[set, str]
        Required modifier keys and the required character key.
    """

    modifiers = set()
    key = None

    for part in hotkey_string.split("+"):
        part = part.strip().lower()

        if part in ("<alt>", "alt"):
            modifiers.add(keyboard.Key.alt)
        elif part in ("<ctrl>", "ctrl"):
            modifiers.add(keyboard.Key.ctrl)
        elif part in ("<shift>", "shift"):
            modifiers.add(keyboard.Key.shift)
        else:
            key = part

    return modifiers, key


def normalize_key(key):
    """
    Convert a pynput key into a canonical value for state tracking.
    """

    if key in ALT_KEYS:
        return keyboard.Key.alt

    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        return keyboard.Key.ctrl

    if key in (keyboard.Key.shift_l, keyboard.Key.shift_r):
        return keyboard.Key.shift

    if hasattr(key, "char") and key.char is not None:
        return key.char.lower()

    if hasattr(key, "vk") and key.vk in (106, 556):
        return GLOBAL_HOTKEY

    return key


def is_hotkey_active(pressed_keys, required_modifiers, required_key):
    """
    Return True when all required keys are currently pressed.
    """

    return (
        required_modifiers.issubset(pressed_keys)
        and required_key in pressed_keys
    )


# ==========================================================================
# OBS manager
# ==========================================================================

class OBSManager:
    """Centralized OBS manager."""

    def __init__(self, sounds):
        """
        Initialize the manager.

        Parameters
        ----------
        sounds : list
            List of Sound objects.
        """

        self.sounds = sounds

        self.client = None
        self.event_client = None

        self.listener = None

        self.hotkey_map = {}
        self.parsed_hotkeys = {}
        self.source_map = {}

        self.pressed_keys = set()
        self.active_hotkeys = set()

        self.hotkeys_enabled = True

    # ------------------------------------------------------------------

    def connect(self):
        """
        Connect to the OBS request client.
        """

        print("Connecting to OBS...")

        self.client = obs.ReqClient(
            host=HOST,
            port=PORT,
            password=PASSWORD
        )

        print("OBS connection established.")

        return self.client

    # ------------------------------------------------------------------

    def connect_events(self):
        """
        Connect to the OBS event client.
        """

        print("Connecting to OBS EventClient...")

        self.event_client = obs.EventClient(
            host=HOST,
            port=PORT,
            password=PASSWORD
        )

        print("OBS EventClient connected.")

        return self.event_client

    # ------------------------------------------------------------------

    def disconnect(self):
        """
        Close every OBS connection.
        """

        if self.listener is not None:
            self.listener.stop()
            self.listener = None

        if self.event_client is not None:
            self.event_client.disconnect()
            self.event_client = None

        if self.client is not None:
            self.client.disconnect()
            self.client = None

    # ------------------------------------------------------------------

    def check_scene_exists(self, scene_name):
        """
        Check that a scene exists.
        """

        print(f"Searching scene: {scene_name}")

        scene_list = self.client.get_scene_list()

        for scene in scene_list.scenes:

            if scene["sceneName"] == scene_name:

                print("Scene found.")
                return True

        raise RuntimeError(
            f"Scene '{scene_name}' was not found."
        )

    # ------------------------------------------------------------------

    def get_scene_item_id(self, scene_name, source_name):
        """
        Return the Scene Item ID of a source.
        """

        self.check_scene_exists(scene_name)

        print(f"Searching source: {source_name}")

        scene_items = self.client.get_scene_item_list(
            scene_name
        )

        for item in scene_items.scene_items:

            if item["sourceName"] == source_name:

                print("Source found.")

                return item["sceneItemId"]

        raise RuntimeError(
            f"Source '{source_name}' was not found."
        )

    # ------------------------------------------------------------------

    def initialize_scene_items(self):
        """
        Initialize every Scene Item ID.
        """

        print("Initializing scene items...")

        for sound in self.sounds:

            sound.scene_item_id = self.get_scene_item_id(
                sound.scene,
                sound.source
            )

        print("Scene items initialized.")

    # ------------------------------------------------------------------

    def build_transform(
        self,
        x=None,
        y=None,
        scale_x=None,
        scale_y=None,
        rotation=None
    ):
        """
        Build a transform dictionary.
        """

        transform = {}

        if x is not None:
            transform["positionX"] = x

        if y is not None:
            transform["positionY"] = y

        if scale_x is not None:
            transform["scaleX"] = scale_x

        if scale_y is not None:
            transform["scaleY"] = scale_y

        if rotation is not None:
            transform["rotation"] = rotation

        return transform

    # ------------------------------------------------------------------

    def apply_transform(self, sound):
        """
        Apply the configured transform to a media source.
        """

        self.client.set_scene_item_transform(

            sound.scene,

            sound.scene_item_id,

            self.build_transform(

                x=sound.x,

                y=sound.y,

                scale_x=sound.scale_x,

                scale_y=sound.scale_y,

                rotation=sound.rotation

            )

        )

    # ------------------------------------------------------------------

    def play_video(self, sound):
        """
        Trigger a configured video source.
        """

        print(f"Playing video '{sound.name}'...")

        self.apply_transform(sound)

        self.client.set_input_volume(

            sound.source,

            sound.volume / 100

        )

        self.client.set_scene_item_enabled(

            sound.scene,

            sound.scene_item_id,

            True

        )

        self.client.trigger_media_input_action(

            sound.source,

            "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"

        )

    # ------------------------------------------------------------------

    def show_image(self, sound):
        """
        Show a configured image source.
        """

        print(f"Showing image '{sound.name}'...")

        self.apply_transform(sound)

        self.client.set_scene_item_enabled(

            sound.scene,

            sound.scene_item_id,

            True

        )

    # ------------------------------------------------------------------

    def hide_image(self, sound):
        """
        Hide a configured image source.
        """

        print(f"Hiding image '{sound.name}'...")

        self.client.set_scene_item_enabled(

            sound.scene,

            sound.scene_item_id,

            False

        )

    # ------------------------------------------------------------------

    def build_hotkeys(self):
        """
        Build the hotkey and source dictionaries.
        """

        print("Building hotkey dictionaries...")

        self.hotkey_map.clear()
        self.parsed_hotkeys.clear()
        self.source_map.clear()

        for sound in self.sounds:

            if sound.hotkey.strip() == GLOBAL_HOTKEY:

                raise ValueError(
                    f"Media '{sound.name}' uses the reserved global hotkey "
                    f"'{GLOBAL_HOTKEY}'."
                )

            if sound.hotkey not in self.hotkey_map:

                self.hotkey_map[sound.hotkey] = []

            self.hotkey_map[sound.hotkey].append(sound)

            self.source_map[sound.source] = sound

        for hotkey in self.hotkey_map:

            self.parsed_hotkeys[hotkey] = parse_hotkey(hotkey)

        print("Hotkey dictionaries created.")

    # ------------------------------------------------------------------

    def print_hotkeys_state(self):
        """
        Print the current media hotkey enabled/disabled state.
        """

        print()
        print("===================================")

        if self.hotkeys_enabled:
            print("HOTKEYS ENABLED")
        else:
            print("HOTKEYS DISABLED")

        print("===================================")
        print()

    # ------------------------------------------------------------------

    def toggle_hotkeys(self):
        """
        Toggle whether configured media hotkeys are allowed to trigger.
        """

        self.hotkeys_enabled = not self.hotkeys_enabled
        self.print_hotkeys_state()

    # ------------------------------------------------------------------

    def on_hotkey_pressed(self, hotkey):
        """
        Handle a hotkey activation event.
        """

        if not self.hotkeys_enabled:
            return

        print()
        print("===================================")
        print(f"Hotkey pressed: {hotkey}")
        print("===================================")

        sounds = self.hotkey_map.get(hotkey)

        if sounds is None:
            return

        for sound in sounds:

            if sound.type == "video":
                self.play_video(sound)

            elif sound.type == "image":
                self.show_image(sound)

    # ------------------------------------------------------------------

    def on_hotkey_released(self, hotkey):
        """
        Handle a hotkey deactivation event.
        """

        print()
        print("===================================")
        print(f"Hotkey released: {hotkey}")
        print("===================================")

        sounds = self.hotkey_map.get(hotkey)

        if sounds is None:
            return

        for sound in sounds:

            if sound.type == "image":
                self.hide_image(sound)

    # ------------------------------------------------------------------

    def evaluate_hotkeys(self):
        """
        Compare configured hotkeys against the current pressed-key state.
        """

        for hotkey, (required_modifiers, required_key) in (
            self.parsed_hotkeys.items()
        ):

            active = is_hotkey_active(
                self.pressed_keys,
                required_modifiers,
                required_key,
            )

            if active and hotkey not in self.active_hotkeys:

                if self.hotkeys_enabled:
                    self.active_hotkeys.add(hotkey)
                    self.on_hotkey_pressed(hotkey)

            elif not active and hotkey in self.active_hotkeys:

                self.active_hotkeys.discard(hotkey)
                self.on_hotkey_released(hotkey)

    # ------------------------------------------------------------------

    def on_key_press(self, key):
        """
        Handle a keyboard press event.
        """

        normalized = normalize_key(key)

        if normalized in self.pressed_keys:
            return

        self.pressed_keys.add(normalized)

        if normalized == GLOBAL_HOTKEY:
            self.toggle_hotkeys()
            return

        self.evaluate_hotkeys()

    # ------------------------------------------------------------------

    def on_key_release(self, key):
        """
        Handle a keyboard release event.
        """

        normalized = normalize_key(key)

        if normalized not in self.pressed_keys:
            return

        self.pressed_keys.discard(normalized)

        if normalized == GLOBAL_HOTKEY:
            return

        self.evaluate_hotkeys()

    # ------------------------------------------------------------------

    def on_media_input_playback_ended(self, data):
        """
        Handle the end of a media playback.
        """

        print()
        print("===================================")
        print("Media playback ended")
        print("===================================")

        sound = self.source_map.get(data.input_name)

        if sound is None:

            print(f"Ignored event ({data.input_name})")
            return

        if sound.type != "video":

            print(
                f"Ignored event for non-video source ({data.input_name})"
            )
            return

        print(f"Source: {data.input_name}")

        self.client.set_scene_item_enabled(

            sound.scene,

            sound.scene_item_id,

            False

        )

        print("Source hidden.")

    # ------------------------------------------------------------------

    def start(self):
        """
        Start the OBS manager.
        """

        print("Initializing OBS manager...")

        self.event_client.callback.register(
            self.on_media_input_playback_ended
        )

        self.pressed_keys.clear()
        self.active_hotkeys.clear()
        self.hotkeys_enabled = True

        self.print_hotkeys_state()

        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release,
        )

        print("OBS manager ready.")
        print()
        print("Registered hotkeys:")

        print(f"  {GLOBAL_HOTKEY} (global enable/disable)")

        for hotkey in self.hotkey_map:

            print(f"  {hotkey}")

        print()
        print("Press Ctrl+C to exit.")
        print()

        self.listener.start()
        self.listener.join()
