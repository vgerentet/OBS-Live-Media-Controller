"""
Application entry point for the Video Soundboard project.
"""

from config import load_sounds
from obs import OBSManager


CONFIG_FILE = "config/config.json"


def main():
    """Start the Video Soundboard application."""

    sounds = load_sounds(CONFIG_FILE)

    manager = OBSManager(sounds)

    try:
        manager.connect()
        manager.connect_events()

        for sound in sounds:
            manager.check_scene_exists(sound.scene)

        manager.initialize_scene_items()
        manager.build_hotkeys()
        manager.start()

    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()