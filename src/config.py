"""
=============================================================================
config.py

Configuration management for the Video Soundboard project.

This module is responsible for:

    - loading the JSON configuration file;
    - validating its content;
    - creating Python objects representing configured sounds.

This module never communicates with OBS Studio and never handles keyboard
shortcuts.

All OBS-related operations are performed by obs.py.
=============================================================================
"""

import json


# =============================================================================
# Sound class
# =============================================================================

class Sound:
    """
    Represents a single sound entry from the configuration file.

    Attributes
    ----------
    name : str
        Friendly name of the sound.

    type : str
        Media type: ``"video"`` or ``"image"``.

    scene : str
        OBS scene containing the source.

    source : str
        OBS media source name.

    hotkey : str
        Keyboard shortcut associated with the sound.

    x : int
        Horizontal position.

    y : int
        Vertical position.

    scale_x : float
        Horizontal scale.

    scale_y : float
        Vertical scale.

    rotation : float
        Rotation angle in degrees.

    volume : int
        Playback volume in percent.

    scene_item_id : int | None
        OBS Scene Item ID.

        This attribute is initialized to None and will later be filled by
        obs.py after the corresponding source has been located in OBS.
    """

    def __init__(
        self,
        name,
        type,
        scene,
        source,
        hotkey,
        x,
        y,
        scale_x,
        scale_y,
        rotation,
        volume
    ):
        self.name = name
        self.type = type
        self.scene = scene
        self.source = source
        self.hotkey = hotkey

        self.x = x
        self.y = y

        self.scale_x = scale_x
        self.scale_y = scale_y

        self.rotation = rotation

        self.volume = volume

        # Filled later by obs.py
        self.scene_item_id = None


# =============================================================================
# JSON loading
# =============================================================================

def load_config(filename):
    """
    Load a JSON configuration file.

    Parameters
    ----------
    filename : str
        Path to the JSON configuration file.

    Returns
    -------
    dict
        Parsed JSON data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    json.JSONDecodeError
        If the file contains invalid JSON.
    """

    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


# =============================================================================
# Configuration validation
# =============================================================================

def validate_config(data):
    """
    Validate the configuration structure.

    The function checks:

        - presence of the "sounds" section;
        - required fields;
        - data types.

    Parameters
    ----------
    data : dict
        Parsed JSON configuration.

    Raises
    ------
    TypeError
        If a value has an invalid type.

    KeyError
        If a required field is missing.

    ValueError
        If the configuration structure is invalid.
    """

    if not isinstance(data, dict):
        raise TypeError("Configuration must be a JSON object.")

    if "sounds" not in data:
        raise KeyError("Missing 'sounds' section.")

    if not isinstance(data["sounds"], list):
        raise TypeError("'sounds' must be a list.")

    required_fields = {
        "name": str,
        "type": str,
        "scene": str,
        "source": str,
        "hotkey": str,
        "x": int,
        "y": int,
        "scale_x": (int, float),
        "scale_y": (int, float),
        "rotation": (int, float),
        "volume": int,
    }

    for index, sound in enumerate(data["sounds"], start=1):

        if not isinstance(sound, dict):
            raise TypeError(
                f"Sound #{index} must be a JSON object."
            )

        for field, expected_type in required_fields.items():

            if field not in sound:
                raise KeyError(
                    f"Missing field '{field}' in sound #{index}."
                )

            if not isinstance(sound[field], expected_type):
                raise TypeError(
                    f"Field '{field}' in sound #{index} has an invalid type."
                )

        if sound["type"] not in ("video", "image"):
            raise ValueError(
                f"Field 'type' in sound #{index} must be 'video' or 'image', "
                f"got {sound['type']!r}."
            )


# =============================================================================
# Object creation
# =============================================================================

def build_sound_objects(data):
    """
    Build Sound objects from validated configuration data.

    Parameters
    ----------
    data : dict
        Validated configuration dictionary.

    Returns
    -------
    list[Sound]
        List of Sound objects.
    """

    sounds = []

    for sound_data in data["sounds"]:

        sound = Sound(
            name=sound_data["name"],
            type=sound_data["type"],
            scene=sound_data["scene"],
            source=sound_data["source"],
            hotkey=sound_data["hotkey"],
            x=sound_data["x"],
            y=sound_data["y"],
            scale_x=sound_data["scale_x"],
            scale_y=sound_data["scale_y"],
            rotation=sound_data["rotation"],
            volume=sound_data["volume"],
        )

        sounds.append(sound)

    return sounds


# =============================================================================
# Public API
# =============================================================================

def load_sounds(filename):
    """
    Load, validate and build the complete sound configuration.

    This is the public entry point of the module.

    Parameters
    ----------
    filename : str
        Path to the JSON configuration file.

    Returns
    -------
    list[Sound]
        List of configured Sound objects.
    """

    data = load_config(filename)
    validate_config(data)
    return build_sound_objects(data)